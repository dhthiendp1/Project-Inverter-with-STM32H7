#ifndef INV_PARK_H
#define INV_PARK_H

#include <math.h>

typedef struct {
    float Vq;
    float Vd;
    float Angle;
    float Valfa;
    float Vbeta;
} InvPark_Transform;

void InvPark_Update(InvPark_Transform *invPark);

#endif