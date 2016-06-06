from conjure.app_config import app
import os


save_path = os.path.join(app.config['spell-dir'], 'results.txt')


def write_results(results):
    results.append("\n")
    results.append("If you need to access these results for the future "
                   "they are stored in: {}".format(save_path))

    with open(save_path, 'w') as fp:
        fp.write("\n".join(results))
