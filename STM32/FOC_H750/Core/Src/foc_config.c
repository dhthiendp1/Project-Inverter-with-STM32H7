#include "foc_config.h"

volatile FOC_Parameters foc_prm;

void FOC_Config_Init(void) {
    foc_prm.Ld = 12.23e-3f;
    foc_prm.Lq = 12.23e-3f;
    foc_prm.R  = 5.83f;
    foc_prm.J  = 0.3e-4f;
    foc_prm.P  = 8;
    foc_prm.Rated_Torque = 1.27f;
    foc_prm.Max_Torque = 3.8f;
    foc_prm.I_Rate = 2.8f;
    foc_prm.I_Max = 3.96f;
    foc_prm.Flux = (4.0f / 3.0f) * (foc_prm.Rated_Torque / ((float)foc_prm.P * foc_prm.I_Rate));
    foc_prm.Vdc = 70.0f;
    foc_prm.U_max = foc_prm.Vdc / 1.73205081f; // Vdc / sqrt(3)
    foc_prm.Iq_max = foc_prm.I_Max;

    // SVPWM
    foc_prm.Fsw = 5000.0f;
    foc_prm.Tsw = 1.0f / foc_prm.Fsw;
    foc_prm.Ts  = 2e-4f;

    // 4. Giá trị PI Dòng điện
    foc_prm.Kp_i = 10.0f;
    foc_prm.Ki_i = 3600.0f;

    // 5. Giá trị PI Tốc độ
    foc_prm.Kp_w = 1.0f;
    foc_prm.Ki_w = 100.0f;

    foc_prm.Apply_New_Tuning = 0;
}
