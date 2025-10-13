#include "ControllLoop.c"

// Function Clark Park

void Calculate_Park_Go(Output_Park_Go *pointer_Park_Go, PI_Iq_ctrl_Init *pointer_Iq_ctrl, PI_Iq_ctrl_Init pointer_Iq_ctrl, float Angle_input);
void Calculate_Park_Back();
void Calculate_Clark_Back();

// Struct FOC (SVPWM Controller)

void Calculate_Polar_Form(Polar_Form *Output, const Output_Park_Go *Input);
void Time_Calculator_Update(Time_Calculator *Output, const Polar_Form *Input);
void SPWM_Controller_Update(SPWM_Controller *Output, const Time_Calculator* Input);
