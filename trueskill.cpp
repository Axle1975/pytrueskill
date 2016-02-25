#include "trueskill.h"
#include "gaussian.h"
#include "truncated_gaussian.h"
#include <cmath>

namespace trueskill
{
	double quality_1vs1(const double *env,
		const double *r1,
		const double *r2)
	{
		const double sigmasq1 = r1[SIGMA]*r1[SIGMA];
		const double sigmasq2 = r2[SIGMA]*r2[SIGMA];
		const double betasq = env[BETA]*env[BETA];
		const double denominator = 2*betasq + sigmasq1 + sigmasq2;

		double q = r1[MU] - r2[MU];
		q *= q/denominator/2.0;
		q = std::exp(-q);
		q *= std::sqrt(2.0*betasq/denominator);
		return q;
	}


	double win_probability_1vs1(const double *env,
		const double *r1,
		const double *r2)
	{
		const double sigmasq1 = r1[SIGMA]*r1[SIGMA];
		const double sigmasq2 = r2[SIGMA]*r2[SIGMA];
		const double betasq = env[BETA]*env[BETA];
		const double denominator = std::sqrt(2*betasq + sigmasq1 + sigmasq2);
		return norm_cdf( (r1[MU]-r2[MU]) / denominator );
	}

	double draw_margin(const double *env)
	{
		// Derived from TrueSkill technical report (MSR-TR-2006-80), page 6
		// draw probability = 2 * CDF(margin/(sqrt(n1+n2)*beta)) -1
		// implies
		//
		// margin = inversecdf((draw probability + 1)/2) * sqrt(n1+n2) * beta
		// n1 and n2 are the number of players on each team

		return norm_ppf(0.5*(env[PDRAW]+1.0)) * std::sqrt(2.0) * env[BETA];
	}
	
	double pdraw(const double *env,
		const double *r1,
		const double *r2)
	{
		double eps = draw_margin(env);
		double mu = r1[MU] - r2[MU];
		double sigma = std::sqrt(r1[SIGMA]*r1[SIGMA] + r2[SIGMA]*r2[SIGMA] + 2.0*env[BETA]*env[BETA]);
		return norm_cdf((eps-mu)/sigma) - norm_cdf((-eps-mu)/sigma);
	}

	double pwin(const double *env,
		const double *r1,
		const double *r2)
	{
		double eps = draw_margin(env);
		double mu = r1[MU] - r2[MU];
		double sigma = std::sqrt(r1[SIGMA]*r1[SIGMA] + r2[SIGMA]*r2[SIGMA] + 2.0*env[BETA]*env[BETA]);
		return 1.0 - norm_cdf((eps-mu)/sigma);
	}

	double plose(const double *env,
		const double *r1,
		const double *r2)
	{
		double eps = draw_margin(env);
		double mu = r1[MU] - r2[MU];
		double sigma = std::sqrt(r1[SIGMA]*r1[SIGMA] + r2[SIGMA]*r2[SIGMA] + 2.0*env[BETA]*env[BETA]);
		return norm_cdf((-eps-mu)/sigma);
	}

	double likelihood_outcome_1vs1(
		const double *env,
		const int score12,
		const double *r1,
		const double *r2)
	{
		//double pdraw = env[PDRAW] * quality_1vs1(env,r1,r2);
		if (score12 > 0)
		{
			return pwin(env,r1,r2);
			//return (1.0-pdraw) * win_probability_1vs1(env,r1,r2);
		}
		else if (score12 == 0)
		{
			return pdraw(env,r1,r2);
			//return pdraw;
		}
		else
		{
			return plose(env,r1,r2);
		}
	}


	void rate_1vs1(const double *env,
		const int score12,
		double *r1,
		double *r2)
	{
		double drawMargin = draw_margin(env);
		double c = std::sqrt(r1[SIGMA]*r1[SIGMA] +
			r2[SIGMA]*r2[SIGMA] +
			2.0*env[BETA]*env[BETA]);

		double rankMultiplier;
		double v, w;
		if (score12 < 0) {
			rankMultiplier = -1.0;
			v = VExceedsMargin(r2[MU]-r1[MU], drawMargin, c);
			w = WExceedsMargin(r2[MU]-r1[MU], drawMargin, c);
		}
		else if (score12 == 0) {
			rankMultiplier = 1.0;
			v = VWithinMargin(r1[MU]-r2[MU], drawMargin, c);
			w = WWithinMargin(r1[MU]-r2[MU], drawMargin, c);
		}
		else {
			rankMultiplier = 1.0;
			v = VExceedsMargin(r1[MU]-r2[MU], drawMargin, c);
			w = WExceedsMargin(r1[MU]-r2[MU], drawMargin, c);
		}

		// update r1
		double varianceWithDynamics = r1[SIGMA]*r1[SIGMA] + env[TAU]*env[TAU];
		double meanMultiplier = varianceWithDynamics / c;
		double stdDevMultiplier = meanMultiplier / c;

		r1[MU] = r1[MU] + rankMultiplier*meanMultiplier*v;
		r1[SIGMA] = std::sqrt(varianceWithDynamics*(1.0 - w*stdDevMultiplier));

		// update r2
		varianceWithDynamics = r2[SIGMA]*r2[SIGMA] + env[TAU]*env[TAU];
		meanMultiplier = varianceWithDynamics / c;
		stdDevMultiplier = meanMultiplier / c;

		r2[MU] = r2[MU] - rankMultiplier*meanMultiplier*v;
		r2[SIGMA] = std::sqrt(varianceWithDynamics*(1.0 - w*stdDevMultiplier));
	}

}