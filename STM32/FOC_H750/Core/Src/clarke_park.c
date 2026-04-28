#include "clarke_park.h"

#define SQRT3_INV 0.577350269f

void ClarkePark_Update(ClarkePark_Transform *cp) {
    float i_alpha = cp->Ia;
    float i_beta  = (SQRT3_INV * cp->Ia) + (2.0f * SQRT3_INV * cp->Ib);
    
    float cos_t = cos(cp->Angle);
    float sin_t = sin(cp->Angle);
    
    cp->Id =  (i_alpha * cos_t) + (i_beta * sin_t);
    cp->Iq = -(i_alpha * sin_t) + (i_beta * cos_t);
}