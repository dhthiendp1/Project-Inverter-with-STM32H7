#ifndef PI_TUSTIN_H
#define PI_TUSTIN_H

#include <stdbool.h>

typedef struct {
    float Kp;
    float Ki;
    float Ts;          
    float uMax;         
    float uMin;         

    /* Hệ số Tustin */
    float alpha_a;           // Hệ số cho e[k]
    float beta_b;           // Hệ số cho e[k-1]

    /* Biến trạng thái */
    float e_prev;       // e[k-1]
    float u_prev;       // u[k-1]

    bool antiWindup;  
} PI_Tustin_Handler;

void PI_Tustin_Init(PI_Tustin_Handler *pi, float Kp, float Ki, float Ts, float uMax, float uMin);
float PI_Tustin_Update(PI_Tustin_Handler *pi, float target, float measure);
void PI_Tustin_Reset(PI_Tustin_Handler *pi);

#endif