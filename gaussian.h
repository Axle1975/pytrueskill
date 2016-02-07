#pragma once

namespace trueskill
{
	// normal probability density function
	double norm_pdf(double x);

	// normal cumulative probability density function
	double norm_cdf(double x);

	// inverse normal cumulative probability density function (probit)
	double norm_ppf(double x);
}
