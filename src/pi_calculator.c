#include "pi_calculator.h"

void PI_Calc_Current(Motor_Params* params, PI_Parameters* current_pi) {
    params->Ke = 1.0f / params->R;
    params->Kc = (2.0f / 3.0f) * (params->Vdc / params->PWM_Max);
    params->Ti = params->L / params->R;
    current_pi->Kp = params->L / (2.0f * params->Kc * params->Ke * params->Td);
    current_pi->Ki = current_pi->Kp / params->Ti;
}

void PI_Calc_Speed(Motor_Params* params, PI_Parameters* speed_pi) {
    speed_pi->Kp = params->m / (16.0f * params->CFN3 * params->Td);
    speed_pi->Ki = speed_pi->Kp / (8.0f * params->Td);
}