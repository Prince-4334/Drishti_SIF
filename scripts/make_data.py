from drishtisif.model import TRAIN_FILE
from drishtisif.synthetic import make_reports

make_reports(2600, seed=7, with_dates=False, label_noise=0.03).to_csv(TRAIN_FILE, index=False)
make_reports(420, seed=21).drop(columns=["sif_label", "true_rule"]).to_csv("data/demo_reports.csv", index=False)
