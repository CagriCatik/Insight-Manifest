# test_coverage_project/plotter.py
import os
import logging
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)

def create_heatmap(df, output_path, figsize=(10,8), cmap="viridis", title="Test Coverage Matrix"):
    """Create and save a heatmap from the DataFrame."""
    try:
        plt.figure(figsize=figsize)
        ax = sns.heatmap(df, annot=True, fmt="d", cmap=cmap)
        ax.set_title(title)
        ax.set_xlabel("Modules")
        ax.set_ylabel("Test Cases")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path)
        plt.close()
        logger.info("Heatmap saved successfully to %s", output_path)
    except Exception as e:
        logger.exception("Error generating heatmap: %s", e)
        raise

def create_interactive_plot(df):
    """Stub for interactive plot generation (e.g., using Plotly or Bokeh)."""
    logger.info("Interactive plot function called. Not implemented yet.")
