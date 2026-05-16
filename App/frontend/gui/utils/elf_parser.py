from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection

class ElfParser:
    @staticmethod
    def parse_elf_file(file_path):
        symbols_dict = {}
        try:
            with open(file_path, 'rb') as f:
                elffile = ELFFile(f)

                for section in elffile.iter_sections():
                    if isinstance(section, SymbolTableSection):
                        for symbol in section.iter_symbols():
                            if symbol['st_info']['type'] == 'STT_OBJECT' and symbol['st_size'] > 0:
                                var_name = symbol.name
                                byte_size = symbol['st_size']
                                auto_type = "float32" if byte_size == 4 else ("int16" if byte_size == 2 else "uint8")
                                symbols_dict[var_name] = {"addr": hex(symbol['st_value']), "type": auto_type}

                if elffile.has_dwarf_info():
                    print("[ELF Explorer] Đang bóc tách phân vùng DWARF để tìm Type chuẩn...")
                    dwarfinfo = elffile.get_dwarf_info()
                    for CU in dwarfinfo.iter_CUs():
                        die_by_offset = {die.offset: die for die in CU.iter_DIEs()}
                        for die in die_by_offset.values():
                            if die.tag == 'DW_TAG_variable' and 'DW_AT_name' in die.attributes:
                                var_name = die.attributes['DW_AT_name'].value.decode('utf-8', errors='ignore')
                                if var_name in symbols_dict and 'DW_AT_type' in die.attributes:
                                    type_offset = die.attributes['DW_AT_type'].value + CU.cu_offset
                                    base_type_die = ElfParser._resolve_dwarf_type(die_by_offset, type_offset)

                                    if base_type_die and 'DW_AT_name' in base_type_die.attributes:
                                        raw_type_name = base_type_die.attributes['DW_AT_name'].value.decode('utf-8', errors='ignore').lower()

                                        if "float" in raw_type_name: mapped_type = "float32"
                                        elif "unsigned char" in raw_type_name or "uint8" in raw_type_name: mapped_type = "uint8"
                                        elif "char" in raw_type_name or "int8" in raw_type_name: mapped_type = "int8"
                                        elif "unsigned short" in raw_type_name or "uint16" in raw_type_name: mapped_type = "uint16"
                                        elif "short" in raw_type_name or "int16" in raw_type_name: mapped_type = "int16"
                                        elif "unsigned int" in raw_type_name or "uint32" in raw_type_name or "unsigned long" in raw_type_name: mapped_type = "uint32"
                                        else: mapped_type = "int32"

                                        symbols_dict[var_name]["type"] = mapped_type
        except Exception as e:
            print(f"Lỗi phân tích file ELF/DWARF: {e}")
        return symbols_dict

    @staticmethod
    def _resolve_dwarf_type(die_by_offset, type_offset):
        current_die = die_by_offset.get(type_offset)
        while current_die:
            if current_die.tag == 'DW_TAG_base_type':
                return current_die
            elif current_die.tag in ('DW_TAG_typedef', 'DW_TAG_const_type', 'DW_TAG_volatile_type'):
                if 'DW_AT_type' in current_die.attributes:
                    next_offset = current_die.attributes['DW_AT_type'].value + current_die.cu.cu_offset
                    current_die = die_by_offset.get(next_offset)
                else:
                    break
            else:
                break
        return None