

def write_results(results, save_path):
    output = []
    for k, v in results.items():
        output.append("{}: {}".format(k, v))
        output.append("\n")
    output.append("If you need to access these results for the future "
                  "they are stored in: {}".format(save_path))

    with open(save_path, 'w') as fp:
        fp.write("\n".join(output))
    return "\n".join(output)
