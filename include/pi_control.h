#ifndef PI_CONTROL_H
#define PI_CONTROL_H

typedef struct {
    float Kp;   
    float Ki;        
    float Ts;      
    float UpperLimit;  
    float LowerLimit;  
    float Integral;    // (I_prev)
} PI_Clamping;

void PI_Init(PI_Clamping *pi, float kp, float ki, float ts, float max, float min);
float PI_Update(PI_Clamping *pi, float reference, float measured);
void PI_Reset(PI_Clamping *pi);

#endif