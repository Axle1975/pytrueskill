#pragma once

namespace trueskill
{
	double VExceedsMargin(double delta_mu, double drawMargin, double c);
	double WExceedsMargin(double delta_mu, double drawMargin, double c);
	double VWithinMargin(double delta_mu, double drawMargin, double c);
	double WWithinMargin(double delta_mu, double drawMargin, double c);

	double VExceedsMargin(double delta_mu, double drawMargin);
	double WExceedsMargin(double delta_mu, double drawMargin);
	double VWithinMargin(double delta_mu, double drawMargin);
	double WWithinMargin(double delta_mu, double drawMargin);
}