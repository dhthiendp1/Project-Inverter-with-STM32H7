#include "FOC.h"
#include <stdint.h> 

// Function Clack Park

void Calculate_Park_Go(Output_Park_Go *pointer_Park_Go, PI_Iq_ctrl_Init *pointer_Iq_ctrl, PI_Iq_ctrl_Init *pointer_Iq_ctrl, float Angle_input) {
    float u1 = pointer_Iq_ctrl->Vq_output;
    float u2 = pointer_Id_ctrl->Vd_output;
    float u3 = Angle_input;
    // Fcn Park Go
    pointer_Park_Go->V_alfa = cos(u3)*u2 - sin(u3)*u1;
    pointer_Park_Go->V_beta = sin(u3)*u2 + cos(u3)*u1;
}

// Function SVPWM Controller

void Calculate_Polar_Form(Polar_Form *Output, const Output_Park_Go *Input) {
    float u1 = Input->V_alfa;
    float u2 = Input->V_beta;
    float y1 = sqrtf(u1*u1+u2*u2);  // Vref
    float y2 = atan2f(u2,u1);       // Angle
    // Chon Sector
    float s_sector = y2 * (180/M_PI); // Rad to Deg
    if (s_sector < -180.0f || s_sector >= 180.0f) {
        s_sector = 0;
    }
    if (s_sector < 0.0f) {
        s_sector += 360.0f;
    }
    Output->Select_Sector = floorf((s_sector / 60.0f)) + 1.0f;
    Output->V_ref = y1;
    Output->Angle = y2;
}

void Time_Calculator_Update(Time_Calculator *Output, const Polar_Form *Input) {
    float u1 = Input->V_ref;
    float u2 = Input->Angle; // Don vi Rad 
    float u3 = Input->Select_Sector; // section
    float k = (Output->T_period * M_SQRT3) / Output->Vdc; 
    float Ta = k*(u1*sinf(M_PI*u3/3-u2));
    float Tb = k*u1*sinf(u2-(u3-1)*M_PI/3);
    Output->T1 = Ta;  // u1
    Output->T0 = Output->T_period - Ta - Tb; // u2
    Output->T2 = Tb;  // u3
    Output->u = Input->T_period - Ta/2;
    Output->v = Tb/2 + Output->T0;
    Output->w = Tb/2;
    Output->g = Tb/2 + Ta;
    if (u3 < 1 || u3 > 6) {
        Output->Ts1 = 0.0f;
        Output->Ts2 = 0.0f;
        Output->Ts3 = 0.0f;
    }
    static const int matrix[6][3] = { //0=u, 1=v, 2=w, 3=g, cột [Ts1, Ts2, Ts3]
        {0, 1, 2},  // Sector 1 [u, v, w]
        {3, 0, 2},  // Sector 2 [g, u, w]
        {2, 0, 1},  // Sector 3 [w, u, v]
        {2, 3, 0},  // Sector 4 [w, g, u]
        {1, 2, 0},  // Sector 5 [v, w, u]
        {0, 2, 3},  // Sector 6 [u, w, g] 
    };
    float a[] = {Output->u, Output->v, Output->w, Output->g};
    const int *b = matrix[s - 1];
    Output->Ts1 = a[b[0]];
    Output->Ts2 = a[b[1]];
    Output->Ts3 = a[b[2]];
}

void SPWM_Controller_Update(SPWM_Controller *Output, const Time_Calculator* Input) {

}