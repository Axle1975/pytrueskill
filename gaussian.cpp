#include "gaussian.h"
#include <sstream>
#include <cmath>

namespace trueskill
{

	static double erfc(double x)
	{
		// Derived from page 265 of Numerical Recipes 3rd Edition            
		double z = std::abs(x);

		double t = 2.0/(2.0 + z);
		double ty = 4*t - 2;

		double coefficients[] = {
			-1.3026537197817094, 6.4196979235649026e-1,
			1.9476473204185836e-2, -9.561514786808631e-3, -9.46595344482036e-4,
			3.66839497852761e-4, 4.2523324806907e-5, -2.0278578112534e-5,
			-1.624290004647e-6, 1.303655835580e-6, 1.5626441722e-8, -8.5238095915e-8,
			6.529054439e-9, 5.059343495e-9, -9.91364156e-10, -2.27365122e-10,
			9.6467911e-11, 2.394038e-12, -6.886027e-12, 8.94487e-13, 3.13092e-13,
			-1.12708e-13, 3.81e-16, 7.106e-15, -1.523e-15, -9.4e-17, 1.21e-16, -2.8e-17
		};

		int ncof = sizeof(coefficients)/sizeof(double);
		double d = 0.0;
		double dd = 0.0;


		for (int j = ncof - 1; j > 0; j--)
		{
			double tmp = d;
			d = ty*d - dd + coefficients[j];
			dd = tmp;
		}

		double ans = t*std::exp(-z*z + 0.5*(coefficients[0] + ty*d) - dd);
		return x >= 0.0 ? ans : (2.0 - ans);
	}


	static double ierfc(double p)
	{
		// From page 265 of numerical recipes                       

		if (p >= 2.0)
		{
			return -100;
		}
		if (p <= 0.0)
		{
			return 100;
		}

		double pp = (p < 1.0) ? p : 2 - p;
		double t = std::sqrt(-2*std::log(pp/2.0)); // Initial guess
		double x = -0.70711*((2.30753 + t*0.27061)/(1.0 + t*(0.99229 + t*0.04481)) - t);

		for (int j = 0; j < 2; j++)
		{
			double err = erfc(x) - pp;
			x += err/(1.12837916709551257*std::exp(-(x*x)) - x*err); // Halley                
		}

		return p < 1.0 ? x : -x;
	}


	double norm_pdf(double x)
	{
		static const double sqrt2pi = std::sqrt(2*3.1415926535898);
		return std::exp(-x*x/2.0) / sqrt2pi;
	}

	double norm_cdf(double x)
	{
		static const double sqrt1_2 = std::sqrt(0.5);
		return 0.5 * erfc(-sqrt1_2*x);
	}

	double norm_ppf(double x)
	{
		static const double sqrt2 = std::sqrt(2.0);
		return -sqrt2*ierfc(2.0*x);
	}

}