import json
import os

CONFIG_FILE = "block_mapping.json"

def load_mapping():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except: return {}
    return {}

def save_mapping(mapping_data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(mapping_data, f, indent=4)

def add_var_to_block(mapping_data, block_name, var_name, var_addr, var_type):
    if block_name not in mapping_data: mapping_data[block_name] = []
    # Cập nhật nếu đã có, hoặc thêm mới
    found = False
    for v in mapping_data[block_name]:
        if v['id'] == var_name:
            v['addr'] = var_addr; v['type'] = var_type
            found = True; break
    if not found:
        mapping_data[block_name].append({'id': var_name, 'addr': var_addr, 'type': var_type})
    save_mapping(mapping_data)
    return mapping_data

def remove_var_from_block(mapping_data, block_name, var_name):
    if block_name in mapping_data:
        mapping_data[block_name] = [v for v in mapping_data[block_name] if v['id'] != var_name]
        save_mapping(mapping_data)
    return mapping_data