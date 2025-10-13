#include "ControllLoop.h"
#include <math.h>

// Convert deg to rad

float Convert_d2r(float Input)
{
    return Input*((2f*M_PI)/60f)
}

// Function PI Controll Loop

float PI_Speed_Controller_Update(PI_Speed_Controller *pointer_controller, float input) {
    float p_out = pointer_controller->Kp * input;
    pointer_controller->integral_value += (pointer_controller->Ki_Ts * input);

    // Integrator anti-windup
    if (pointer_controller->integral_value > pointer_controller->Integrator_upper) {
        pointer_controller->integral_value = pointer_controller->Integrator_upper;
    } else if (pointer_controller->integral_value < pointer_controller->Integrator_lower) {
        pointer_controller->integral_value = pointer_controller->Integrator_lower;
    }

    float y_presat = p_out + pointer_controller->integral_value;

    // saturation
    if (y_presat > pointer_controller->Sat_max) {
        pointer_controller->output = pointer_controller->Sat_max;
    } else if (y_presat < pointer_controller->Sat_min) {
        pointer_controller->output = pointer_controller->Sat_min;
    } else {
        pointer_controller->output = y_presat;
    }

    return pointer_controller->output;
}

float PI_Iq_ctrl_Update(PI_Iq_ctrl_Init *pointer_Iq_ctrl, float input) {
    float p_out = pointer_Iq_ctrl->Kp_i * input;
    pointer_Iq_ctrl->integral_value += (pointer_Iq_ctrl->Ki_Ts * input);

    // Integrator anti-windup
    if (pointer_Iq_ctrl->integral_value > pointer_Iq_ctrl->Integrator_upper) {
        pointer_Iq_ctrl->integral_value = pointer_Iq_ctrl->Integrator_upper;
    } else if (pointer_Iq_ctrl->integral_value < pointer_Iq_ctrl->Integrator_lower) {
        pointer_Iq_ctrl->integral_value = pointer_Iq_ctrl->Integrator_lower;
    }

    float y_presat = p_out + pointer_Iq_ctrl->integral_value;

    // saturation
    if (y_presat > pointer_Iq_ctrl->Saturation_upper) {
        pointer_Iq_ctrl->Vq_output = pointer_Iq_ctrl->Saturation_upper;
    } else if (y_presat < pointer_Iq_ctrl->Saturation_lower) {
        pointer_Iq_ctrl->Vq_output = pointer_Iq_ctrl->Saturation_lower;
    } else {
        pointer_Iq_ctrl->Vq_output = y_presat;
    }

    return pointer_Iq_ctrl->Vq_output;
}

float PI_Id_ctrl_Update(PI_Id_ctrl_Init *pointer_Id_ctrl, float input) {
    float p_out = pointer_Id_ctrl->Kp_i * input;
    pointer_Id_ctrl->integral_value += (pointer_Id_ctrl->Ki_Ts * input);

    // Integrator anti windup
    if (pointer_Id_ctrl->integral_value > pointer_Id_ctrl->Integrator_upper) {
        pointer_Id_ctrl->integral_value = pointer_Id_ctrl->Integrator_upper;
    } else if (pointer_Id_ctrl->integral_value < pointer_Id_ctrl->Integrator_lower) {
        pointer_Id_ctrl->integral_value = pointer_Id_ctrl->Integrator_lower;
    }

    float y_presat = p_out + pointer_Id_ctrl->integral_value;

    // saturation
    if (y_presat > pointer_Id_ctrl->Saturation_upper) {
        pointer_Id_ctrl->Vd_output = pointer_Id_ctrl->Saturation_upper;
    } else if (y_presat < pointer_Id_ctrl->Saturation_lower) {
        pointer_Id_ctrl->Vd_output = pointer_Id_ctrl->Saturation_lower;
    } else {
        pointer_Id_ctrl->Vd_output = y_presat;
    }

    return pointer_Id_ctrl->Vd_output;
}
