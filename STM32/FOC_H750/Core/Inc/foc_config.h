#ifndef FOC_CONFIG_H
#define FOC_CONFIG_H

#include <stdint.h>

typedef struct {
    // Motor Parameters
    float Ld;               // [H] Điện cảm trục d
    float Lq;               // [H] Điện cảm trục q
    float R;                // [Ohm] Điện trở stator
    float J;                // [Kg.m^2] Momen quán tính
    int   P;                // Số cực 
    float Flux;             // [Wb] Hệ số từ thông
    float Rated_Torque;     // [N.m] Mô-men định mức
    float Max_Torque;       // [N.m] Mô-men tối đa
    float I_Rate;           // [A] Dòng điện định mức
    float I_Max;            // [A] Dòng điện tối đa

    // System & Limits
    float Vdc;              // [V] Điện áp DC Bus
    float U_max;            // [V] Giới hạn điện áp PI (Vdc / sqrt(3))
    float Iq_max;           // [A] Giới hạn dòng điện PI
    
    //  SVPWM
    float Fsw;              // [Hz] Tần số băm xung SVPWM
    float Tsw;              // [s] Chu kỳ đóng cắt (1 / Fsw)
    float Ts;               // [s] Thời gian lấy mẫu vòng lặp 

    // PI Current
    float Kp_i;
    float Ki_i;

    // PI Speed
    float Kp_w;
    float Ki_w;

    // --- Biến cờ lệnh dùng cho Debug ---
    // Nhập '1' vào biến này trên CubeIDE để ép hệ thống nạp lại thông số mới
    uint8_t Apply_New_Tuning; 

} FOC_Parameters;

// Khai báo biến toàn cục
extern volatile FOC_Parameters foc_prm;

// Hàm khởi tạo giá trị ban đầu
void FOC_Config_Init(void);

#endif /* FOC_CONFIG_H */