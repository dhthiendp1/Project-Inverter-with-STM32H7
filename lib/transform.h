#include <math.h>
typedef struct {
    float Vd;
    float Vq;
    float Theta;  
    float Valpha; 
    float Vbeta;  
} InvPark_Transform;

void InvPark_Update(InvPark_Transform *invPark) {
    float cos_theta = cos(invPark->Theta);
    float sin_theta = sin(invPark->Theta);
    
    invPark->Valpha = (invPark->Vd * cos_theta) - (invPark->Vq * sin_theta);
    invPark->Vbeta  = (invPark->Vd * sin_theta) + (invPark->Vq * cos_theta);
}