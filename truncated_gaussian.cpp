#include "truncated_gaussian.h"
#include "gaussian.h"
#include <cmath>

namespace trueskill
{

	/**
	* @brief  These functions from the bottom of page 4 of the TrueSkill paper.
	* The "V" function where the team performance difference is greater than the draw margin.
	* In the reference F# implementation, this is referred to as "the additive 
	* correction of a single-sided truncated Gaussian with unit variance."
	*/
	double VExceedsMargin(double delta_mu, double drawMargin, double c)
	{
		return VExceedsMargin(delta_mu/c, drawMargin/c);
	}

	double VExceedsMargin(double delta_mu, double drawMargin)
	{
		double denominator = norm_cdf(delta_mu - drawMargin);
		if (denominator < 2.222758749e-162)
		{
			return drawMargin - delta_mu;
		}
		return norm_pdf(delta_mu - drawMargin) / denominator;
	}

	/**
	* @brief The "W" function where the team performance difference is greater than the draw margin.
	* In the reference F# implementation, this is referred to as "the multiplicative
	* correction of a single-sided truncated Gaussian with unit variance."
	*/
	double WExceedsMargin(double delta_mu, double drawMargin, double c)
	{
		return WExceedsMargin(delta_mu/c, drawMargin/c);
	}

	double WExceedsMargin(double delta_mu, double drawMargin)
	{
		double denominator = norm_cdf(delta_mu - drawMargin);
		if (denominator < 2.222758749e-162) {
			if (delta_mu < 0.0) {
				return 1.0;
			}
			return 0.0;
		}
		double vWin = VExceedsMargin(delta_mu, drawMargin, 1.0);
		return vWin*(vWin + delta_mu - drawMargin);
	}

	// the additive correction of a double-sided truncated Gaussian with unit variance
	double VWithinMargin(double delta_mu, double drawMargin, double c)
	{
		return VWithinMargin(delta_mu/c, drawMargin/c);
	}

	double VWithinMargin(double delta_mu, double drawMargin)
	{
		double abs_delta_mu = std::abs(delta_mu);
		double denominator =
			norm_cdf(drawMargin - abs_delta_mu) -
			norm_cdf(-drawMargin - abs_delta_mu);

		if (denominator < 2.222758749e-162) {
			if (delta_mu < 0.0) {
				return -delta_mu - drawMargin;
			}
			return -delta_mu + drawMargin;
		}

		double numerator =
			norm_pdf(-drawMargin - abs_delta_mu) -
			norm_pdf(drawMargin - abs_delta_mu);

		if (delta_mu < 0.0) {
			return -numerator/denominator;
		}
		return numerator/denominator;
	}

	// the multiplicative correction of a double-sided truncated Gaussian with unit variance
	double WWithinMargin(double delta_mu, double drawMargin, double c)
	{
		return WWithinMargin(delta_mu/c, drawMargin/c);
	}

	double WWithinMargin(double delta_mu, double drawMargin)
	{
		double abs_delta_mu = std::abs(delta_mu);
		double denominator =
			norm_cdf(drawMargin - abs_delta_mu) -
			norm_cdf(-drawMargin - abs_delta_mu);

		if (denominator < 2.222758749e-162) {
			return 1.0;
		}

		double vt = VWithinMargin(abs_delta_mu, drawMargin);
		double w1 = drawMargin - abs_delta_mu;
		double w2 = -drawMargin - abs_delta_mu;
		return vt*vt + ( w1*norm_pdf(w1) - w2*norm_pdf(w2) ) / denominator;
	}

}