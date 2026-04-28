#ifndef SVPWM_H
#define SVPWM_H

#include <math.h>

typedef struct {
    float Vdc;
    float Tsw;
    float Valpha;
    float Vbeta;
    int Sector;
    float Ts1;
    float Ts2;
    float Ts3;
} SVPWM_Controller;

void SVPWM_Init(SVPWM_Controller *svpwm, float vdc, float tsw);
void SVPWM_Update(SVPWM_Controller *svpwm);

#endif