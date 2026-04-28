#include "pi_2p2z.h"

void PI_2P2Z_Init(PI_2P2Z_VARS *vars) {
    vars->out1 = 0.0f;
    vars->out2 = 0.0f;
    vars->errn = 0.0f;
    vars->errn1 = 0.0f;
    vars->errn2 = 0.0f;
    vars->ref = 0.0f;
    vars->fdbk = 0.0f;
    vars->out = 0.0f;
}

void PI_2P2Z_Update(PI_2P2Z_COEFFS *coeffs, PI_2P2Z_VARS *vars) {
    float pre_sat_out;
    float hist_out;

    // e(n) = Ref - Fdbk
    vars->errn = vars->ref - vars->fdbk;

    // phương trình sai phân 2P2Z
    pre_sat_out = (coeffs->coeff_a1 * vars->out1) + 
                  (coeffs->coeff_a2 * vars->out2) + 
                  (coeffs->coeff_b0 * vars->errn) + 
                  (coeffs->coeff_b1 * vars->errn1) + 
                  (coeffs->coeff_b2 * vars->errn2);

    // update var
    vars->out2 = vars->out1;
    vars->errn2 = vars->errn1;
    vars->errn1 = vars->errn;

    // Lưu lịch sử đầu ra u(n-1) và i_min và max
    hist_out = pre_sat_out;
    if (hist_out > coeffs->max) {
        hist_out = coeffs->max;
    } else if (hist_out < coeffs->i_min) {
        hist_out = coeffs->i_min;
    }
    vars->out1 = hist_out;

    // last saturation
    vars->out = pre_sat_out;
    if (vars->out > coeffs->max) {
        vars->out = coeffs->max;
    } else if (vars->out < coeffs->min) {
        vars->out = coeffs->min;
    }
}