#include "DefineConst.c"

#ifndef CONTROL_LOOP_H
#define CONTROL_LOOP_H

// Convert rad
float Convert_d2r(float Input);

// Funtion PI Controll Loop

float PI_Speed_Controller_Update(PI_Speed_Controller *pointer_controller, float input);
float PI_iq_ctrl_Update(PI_Iq_ctrl_Init *pointer_Iq_ctrl, float input);
float PI_id_ctrl_Update(PI_Id_ctrl_Init *pointer_Id_ctrl, float input);
