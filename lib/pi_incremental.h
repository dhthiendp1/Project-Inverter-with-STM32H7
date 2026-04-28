#ifndef PI_INCREMENTAL_H
#define PI_INCREMENTAL_H

typedef struct {
    float Kp;          
    float Ki_Ts;       
    float Umax;        
    float Umin;        
    float error_prev;  // Sai số chu kỳ trước e(k-1)
    float out_prev;    // Ngõ ra chu kỳ trước u(k-1)
} PI_Incremental;

void PI_Inc_Init(PI_Incremental *pi, float kp, float ki, float ts, float umax);
float PI_Inc_Update(PI_Incremental *pi, float ref, float meas);
void PI_Inc_Reset(PI_Incremental *pi);
#endif