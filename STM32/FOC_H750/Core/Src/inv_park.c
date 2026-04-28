#include "inv_park.h"

void InvPark_Update(InvPark_Transform *invPark) {
    float cos_t = cos(invPark->Angle);
    float sin_t = sin(invPark->Angle);
    
    invPark->Valfa = (invPark->Vd * cos_t) - (invPark->Vq * sin_t);
    invPark->Vbeta  = (invPark->Vd * sin_t) + (invPark->Vq * cos_t);
}