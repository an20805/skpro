import pymc3 as pm
from sklearn.datasets import load_boston

from skpro.metrics import rank_probability_loss, linearized_log_loss
from skpro.parametric import ParamtericEstimator
from skpro.pymc import PyMC, PlugAndPlayPyMC
from skpro.workflow.manager import DataManager
from skpro.workflow.table import Table

# Load the data
X, y = load_boston(return_X_y=True)
data = DataManager(X, y, name='Boston')


def pymc_linear_regression(model, X, y):
    """Defines a linear regression model in PyMC

    Parameters
    ----------
    model: PyMC model
    X: Features
    y: Labels

    The model must define a ``y_pred`` model variable that represents the prediction target
    """

    with model:
        # Priors
        alpha = pm.Normal('alpha', mu=y.mean(), sd=10)
        betas = pm.Normal('beta', mu=0, sd=10, shape=X.get_value(borrow=True).shape[1])
        sigma = pm.HalfNormal('sigma', sd=1)

        # Model (defines y_pred)
        mu = alpha + pm.math.dot(betas, X.T)
        y_pred = pm.Normal("y_pred", mu=mu, sd=sigma, observed=y)


# Initiate PyMC model
model = PyMC(pymc_model=PlugAndPlayPyMC(pymc_linear_regression))



y_pred = model.fit(data.X_train, data.y_train).predict(data.X_test)

print(rank_probability_loss(y_pred, data.y_test, return_std=True))

from matplotlib import pyplot

pyplot.scatter(y_pred, data.y_test)

pyplot.show()