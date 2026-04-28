#include "pi_control.h"

void PI_Init(PI_Clamping *pi, float kp, float ki, float ts, float max, float min) {
    pi->Kp = kp;
    pi->Ki = ki;
    pi->Ts = ts;
    pi->UpperLimit = max;
    pi->LowerLimit = min;
    pi->Integral = 0.0f;
}

void PI_Reset(PI_Clamping *pi) {
    pi->Integral = 0.0f;
}

float PI_Update(PI_Clamping *pi, float reference, float measured) {
    float error = reference - measured;
    
    // Khâu P
    float p_term = pi->Kp * error;
    
    // output = P + I_prev
    float v = p_term + pi->Integral;
    
    // Saturation
    float u = v;
    if (u > pi->UpperLimit) u = pi->UpperLimit;
    else if (u < pi->LowerLimit) u = pi->LowerLimit;
    
    // Anti-windup 
    // Kiểm tra bão hòa
    int is_saturated = (v != u) ? 1 : 0;
    
    // Kiểm tra cùng dấu
    int same_sign = ((v * error) > 0.0f) ? 1 : 0;
    
    // Nếu Saturated và Same Sign thì không cộng dồn lỗi vào Integrator
    float i_input;
    if (is_saturated && same_sign) {
        i_input = 0.0f; 
    } else {
        i_input = error;
    }
    
    // Cập nhật khâu tích phân cho chu kỳ sau (Forward Euler: Ki * Ts / (z-1))
    pi->Integral += pi->Ki * pi->Ts * i_input;
    
    return u;
}