#ifndef DEFINECONST_H
#define DEFINECONST_H

#define M_PI 3.141592654f
#define M_SQRT3 1.732050810f

// Struct PI Loop

typedef struct {
    float Kp;
    float Ki;
    float Ts;
    float Integrator_upper;
    float Integrator_lower;
    float Saturation_upper;
    float Saturation_lower;
    float integral_value;
    float Ki_Ts; // Tính toán Ki*Ts để tối ưu hoá hàm Update
    float output;
} PI_Speed_Controller;

typedef struct {
    float Kp_i;
    float Ki_i;
    float Ts;
    float Integrator_upper;
    float Integrator_lower;
    float Saturation_upper;
    float Saturation_lower;
    float integral_value;
    float Ki_Ts; // Tính toán Ki*Ts để tối ưu hoá hàm Update
    float Vq_output;
} PI_Iq_ctrl;

typedef struct {
    float Kp_i;
    float Ki_i;
    float Ts;
    float Integrator_upper;
    float Integrator_lower;
    float Saturation_upper;
    float Saturation_lower;
    float integral_value;
    float Ki_Ts; // Tính toán Ki*Ts để tối ưu hoá hàm Update
    float Vd_output;
} PI_Id_ctrl;

// Struct Clack Park
typedef struct {
    float V_alfa;
    float V_beta;
} Output_Park_Go;


// Struct FOC (SVPWM Controller)
typedef struct {
    float V_ref;
    float Angle;
    float Select_Sector;
} Polar_Form;

typedef struct {
    float Tsw1;
    float Tsw2;
    float Tsw3;
    float F_sw;
    float T_period;
    float Vdc;
    float T0;
    float T1;
    float T2;
    float u, v, w, g;
    float Tsw1, Tsw2, Tsw3;
} Time_Calculator;

// Fcn Init 

void PI_Controller_Speed_Init(PI_Speed_Controller *pointer_controller);
void PI_Iq_ctrl_Init(PI_Iq_ctrl *pointer_Iq_ctrl);
void PI_Id_ctrl_Init(PI_Id_ctrl *pointer_Id_ctrl);
void Park_Go_Init(Output_Park_Go *pointer_Park_Go);
void Polar_Form_Init(Polar_Form *pointer_Polar_Form);
void Time_Calculator_Init(Time_Calculator *pointer_Time_Calculator);

endif