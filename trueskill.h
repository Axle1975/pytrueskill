#pragma once

namespace trueskill
{
	// indices into trueskill environment array (MU,SIGMA,BETA,TAU,PDRAW) and also into player rating array (MU and SIGMA only)
	const int MU=0;
	const int SIGMA=1;
	const int BETA=2;
	const int TAU=3;
	const int PDRAW=4;

	/*
	 * @brief calculate 1v1 game quality
	 * @param env c array with trueskill parameters (MU, SIGMA, BETA, TAU and PDRAW)
	 * @param r1 c array with player 1 rating (MU and SIGMA)
	 * @param r2 c array with player 2 rating (MU and SIGMA)
	 */
	double quality_1vs1(
		const double *env,
		const double *r1,
		const double *r2);

	/*
	 * @brief calculate 1v1 probability of win for player 1 given no draw
	 * @param env c array with trueskill parameters (MU, SIGMA, BETA, TAU and PDRAW)
	 * @param r1 c array with player 1 rating (MU and SIGMA)
	 * @param r2 c array with player 2 rating (MU and SIGMA)
	 */
	double win_probability_1vs1(
		const double *env,
		const double *r1,
		const double *r2);

	/*
	 * @brief calculate 1v1 likelihood of game outcome given player ratings
	 * @param env c array with trueskill parameters (MU, SIGMA, BETA, TAU and PDRAW)
	 * @param score12 outcome for which to calculate likelihood. >0 indicates player 1 win, ==0 indicates draw, <0 indicates player 2 win.
	 * @param r1 c array with player 1 rating (MU and SIGMA)
	 * @param r2 c array with player 2 rating (MU and SIGMA)
	 */
	double likelihood_outcome_1vs1(
		const double *env,
		const int score12,
		const double *r1,
		const double *r2);

	/*
	 * @brief update 1v1 player ratings given the outcome of the game
	 * @param env c array with trueskill parameters (MU, SIGMA, BETA, TAU and PDRAW)
	 * @param score12 outcome of game. >0 indicates player 1 win, ==0 indicates draw, <0 indicates player 2 win.
	 * @param r1 c array with player 1 rating (MU and SIGMA)
	 * @param r2 c array with player 2 rating (MU and SIGMA)
	 */
	void rate_1vs1(
		const double *env,
		const int score12,
		double *r1,
		double *r2);

}
