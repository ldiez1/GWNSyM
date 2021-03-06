#ifndef POSRASTER_2D_H
#define POSRASTER_2D_H

#include "lte-user/LteUe.h"
#include "User.h"

/**
 * \description This class updates de user position by moving them in 2D directions making 
 * a grid with a given resolution 
 */
struct PosRaster_2d {

    PosRaster_2d(uint32_t step, uint32_t side, double offset = 0.0)
    : m_step(step)
    , m_side(side)
    , m_offset(offset) {
    }

    void SetIteration(std::uint32_t) {
    }

    void operator()(gnsm::Vec_t<User> us) {
        for (auto i = 0u; i < us.size(); ++i) {
            auto div_ = std::div(int(i * m_step), int(m_side + m_step));
            auto column_ = double(div_.rem);
            auto raw_ = double(div_.quot * m_step);
            us.at(i)->SetPosition({column_ + m_offset, raw_ + m_offset, 1.5});
        }
    }

private:
    const uint32_t m_step;
    const uint32_t m_side;
    const double m_offset;

};

#endif /* POSRASTER_2D_H */