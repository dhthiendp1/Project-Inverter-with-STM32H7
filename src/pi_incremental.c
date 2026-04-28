#include "pi_incremental.h"

void PI_Inc_Init(PI_Incremental *pi, float kp, float ki, float ts, float umax) {
    pi->Kp = kp;
    pi->Ki_Ts = ki * ts; 
    pi->Umax = umax;
    pi->Umin = -umax;
    pi->error_prev = 0.0f;
    pi->out_prev = 0.0f;
}

void PI_Inc_Reset(PI_Incremental *pi) {
    pi->error_prev = 0.0f;
    pi->out_prev = 0.0f;
}

float PI_Inc_Update(PI_Incremental *pi, float ref, float meas) {
    float error = ref - meas;

    // Số add thêm
    // Kp * (e[k] - e[k-1])
    // (Ki * Ts) * e[k]
    float delta_u = pi->Kp * (error - pi->error_prev) + (pi->Ki_Ts * error);

    // u[k] = u[k-1] + delta_u
    float u_k = pi->out_prev + delta_u;

    // Saturation
    if (u_k > pi->Umax)      u_k = pi->Umax;
    else if (u_k < pi->Umin) u_k = pi->Umin;

    pi->error_prev = error;
    pi->out_prev = u_k;

    return u_k;
}