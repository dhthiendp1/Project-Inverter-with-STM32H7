#include "DefinceConst.h"

// Struct PI Loop

void PI_Controller_Speed_Init(PI_Controller_t *pointer_controller) {
    pointer_controller->Kp = 1.0f;
    pointer_controller->Ki = 10.0f;
    pointer_controller->Ts = 2.0e-6f;
    pointer_controller->Integrator_upper = 15.0f;
    pointer_controller->Integrator_lower = -15.0f;
    pointer_controller->Saturation_upper = 3.82f;
    pointer_controller->Saturation_lower = -3.82f;
    pointer_controller->integral_value = 0.0f;
    pointer_controller->output = 0.0f;
    pointer_controller->Ki_Ts = pointer_controller->Ki * pointer_controller->Ts;
}

void PI_Iq_ctrl_Init(PI_Iq_ctrl *pointer_Iq_ctrl) {
    pointer_Iq_ctrl->Kp_i = 3600.0f;
    pointer_Iq_ctrl->Ki_i = 9.36f;
    pointer_Iq_ctrl->Ts = 2.0e-6f;
    pointer_Iq_ctrl->Integrator_upper = 8.5f;
    pointer_Iq_ctrl->Integrator_lower = -8.5f;
    pointer_Iq_ctrl->Saturation_upper = 2000.0f;
    pointer_Iq_ctrl->Saturation_lower = -2000.0f;
    pointer_Iq_ctrl->integral_value = 0.0f;
    pointer_Iq_ctrl->Vq_output = 0.0f;
    pointer_Iq_ctrl->Ki_Ts = pointer_Iq_ctrl->Ki_i * pointer_Iq_ctrl->Ts;
}

void PI_Id_ctrl_Init(PI_Id_ctrl *pointer_Id_ctrl) {
    pointer_Id_ctrl->Kp_i = 3600.0f;
    pointer_Id_ctrl->Ki_i = 9.36f;
    pointer_Id_ctrl->Ts = 2.0e-6f;
    pointer_Id_ctrl->Integrator_upper = 8.5f;
    pointer_Id_ctrl->Integrator_lower = -8.5f;
    pointer_Id_ctrl->Saturation_upper = 2000.0f;
    pointer_Id_ctrl->Saturation_lower = -2000.0f;
    pointer_Id_ctrl->integral_value = 0.0f;
    pointer_Id_ctrl->Vd_output = 0.0f;
    pointer_Id_ctrl->Ki_Ts = pointer_Id_ctrl->Ki_i * pointer_Id_ctrl->Ts;
}

// Struct Clack Park
void Park_Go_Init(Output_Park_Go *pointer_Park_Go) {
    pointer_Park_Go->V_alfa = 0.0f;
    pointer_Park_Go->V_beta = 0.0f;
}

// Struct FOC (SVPWM Controller)

void Polar_Form_Init(Polar_Form *pointer_Polar_Form) {
    pointer_Polar_Form->V_ref = 0.0f;
    pointer_Polar_Form->Angle = 0.0f;
}

void Time_Calculator_Init(Time_Calculator *pointer_Time_Calculator) {
    pointer_Time_Calculator->Tsw1 = 0.0f;
    pointer_Time_Calculator->Tsw2 = 0.0f;
    pointer_Time_Calculator->Tsw3 = 0.0f;
    pointer_Time_Calculator->F_sw = 10000.0f;
    pointer_Time_Calculator->T_period = 1.0f / pointer_Time_Calculator->F_sw;
    pointer_Time_Calculator->Vdc = 500.0f;
    pointer_Time_Calculator->T0 = 0.0f;
    pointer_Time_Calculator->T1 = 0.0f;
    pointer_Time_Calculator->T2 = 0.0f;
}

void SPWM_Controller_Init(SPWM_Controller *pointer_SPWM_Controller) {
    pointer_SPWM_Controller->uPos = 0.0f;
    pointer_SPWM_Controller->uNeg = 0.0f;
    pointer_SPWM_Controller->vPos = 0.0f;
    pointer_SPWM_Controller->vNeg = 0.0f;
    pointer_SPWM_Controller->wPos = 0.0f;
    pointer_SPWM_Controller->wNeg = 0.0f;
}