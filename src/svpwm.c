#include "svpwm.h"

#define PI 3.14159265359f
#define SQRT3 1.73205080757f

void SVPWM_Init(SVPWM_Controller *svpwm, float vdc, float tsw) {
    svpwm->Vdc = vdc;
    svpwm->Tsw = tsw;
}

void SVPWM_Update(SVPWM_Controller *svpwm) {
    //Calcu_Vref & Angle
    float vref = sqrt((svpwm->Valpha * svpwm->Valpha) + (svpwm->Vbeta * svpwm->Vbeta));
    float angle_rad = atan2(svpwm->Vbeta, svpwm->Valpha);
     
    // saturation
    float vref_max = svpwm->Vdc / SQRT3;
    if (vref > vref_max) {
        vref = vref_max; 
    }
    else if (vref < 0) {
        vref = 0;
    }
    // select sector
    float angle_deg = angle_rad * (180.0f / PI);
    int sector = 0;
    
    if (angle_deg >= 0 && angle_deg < 60) sector = 1;
    else if (angle_deg >= 60 && angle_deg < 120) sector = 2;
    else if (angle_deg >= 120 && angle_deg <= 180) sector = 3;
    else if (angle_deg >= -180 && angle_deg < -120) sector = 4;
    else if (angle_deg >= -120 && angle_deg < -60) sector = 5;
    else if (angle_deg >= -60 && angle_deg < 0) sector = 6;
    svpwm->Sector = sector;
    // Calcu_Time
    // a. Time Calculation
    if (sector != 0) {
        float coeff = (svpwm->Tsw*SQRT3*vref)/(svpwm->Vdc);
        float ta = coeff * sin((PI * sector / 3.0f) - angle_rad);
        float tb = coeff * sin(angle_rad - (((sector - 1)*PI)/ 3.0f));
        float t0 = svpwm->Tsw - ta - tb;
     // b. trung gian   
        float u = svpwm->Tsw - (t0 / 2.0f);
        float v = (t0 / 2.0f) + tb;
        float w = t0 / 2.0f;
        float g = (t0 / 2.0f) + ta;
     // c. Time Calcu   
        switch (sector) {
            case 1: svpwm->Ts1 = u; svpwm->Ts2 = v; svpwm->Ts3 = w; break;
            case 2: svpwm->Ts1 = g; svpwm->Ts2 = u; svpwm->Ts3 = w; break;
            case 3: svpwm->Ts1 = w; svpwm->Ts2 = u; svpwm->Ts3 = v; break;
            case 4: svpwm->Ts1 = w; svpwm->Ts2 = g; svpwm->Ts3 = u; break;
            case 5: svpwm->Ts1 = v; svpwm->Ts2 = w; svpwm->Ts3 = u; break;
            case 6: svpwm->Ts1 = u; svpwm->Ts2 = w; svpwm->Ts3 = g; break;
            default: svpwm->Ts1 = 0; svpwm->Ts2 = 0; svpwm->Ts3 = 0; break;
        }
    } else {
        svpwm->Ts1 = 0; 
        svpwm->Ts2 = 0; 
        svpwm->Ts3 = 0;
    }
}