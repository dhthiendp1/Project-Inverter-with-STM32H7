#ifndef SVPWM_DEADBAND_H
#define SVPWM_DEADBAND_H

typedef struct {
    float DeadBand;
    float Ts_sample;

    int prev_raw_u;
    int prev_raw_v;
    int prev_raw_w;
    
    float timer_u;
    float timer_v;
    float timer_w;
    
    float uPos;
    float uNeg;
    float vPos;
    float vNeg;
    float wPos;
    float wNeg;
} ePWM_DeadBand;

void ePWM_DeadBand_Init(ePWM_DeadBand *epwm, float db, float ts);
void ePWM_DeadBand_Update(ePWM_DeadBand *epwm, float ts1, float ts2, float ts3, float carrier);

#endif