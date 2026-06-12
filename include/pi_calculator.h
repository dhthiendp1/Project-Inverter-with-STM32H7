#ifndef PI_CALCULATOR_H
#define PI_CALCULATOR_H

#include <math.h>

typedef struct {
    float L;          //H
    float R;          //Ohm
    float Vdc;        //V DC Bus 
    float PWM_FREQ;   // Hz
    float Tss;
    float Td;
    float Ke;
    float Kc;
    float Ti;
    float m;      
    float CFN3;
} Motor_Params;

typedef struct {
    float Kp;
    float Ki;
} PI_Parameters;

void PI_Calc_Current(Motor_Params* params, PI_Parameters* current_pi);
void PI_Calc_Speed(Motor_Params* params, PI_Parameters* speed_pi);

#endif // PI_CALCULATOR_H

/*
Motor_Params Motor_E_params = {
        .L = MOTOR_LS,     
        .R = MOTOR_LS,         
        .Vdc = VDC_BUS,       
        .PWM_FREQ = MOTOR_PWM_FREQ, 
        .Tss = MOTOR_Tss,       
        .m = MOTOR_m,       
        .CFN3 = MOTOR_CFN3
};

PI_Parameters pi_current;
PI_Parameters pi_speed;

PI_Calc_Current(&Motor_E_params, &pi_current);
PI_Calc_Speed(&Motor_E_params, &pi_speed);
*/