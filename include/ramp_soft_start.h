#ifndef RAMP_SOFT_START_H
#define RAMP_SOFT_START_H

#include <math.h>

typedef struct {
    float Target_rads;   // (rad/s)
    float Current_rads;  // (rad/s)
    float Slope;         // Độ dốc/Gia tốc (rad/s^2)
    float Ts;            
    float Step;          
} Ramp_Struct;

void Ramp_Init(Ramp_Struct *r, float Ts, float slope_rads2);
float Ramp_Update(Ramp_Struct *r, float target_rads);
// slope_rads2 = tan(angle_deg * PI / 180)
#endif