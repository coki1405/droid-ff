import fuzzerConfig
import os


def radamsa_do(sample_path,extension,num_sample):
    cmd = fuzzerConfig.path_to_fuzzer_binaries + "radamsa " \
            + sample_path + " -o " + fuzzerConfig.path_to_generated_samples + \
            "sample%n" + extension + " -n " + str(num_sample)
    os.system(cmd)

    print "done"

def start():
    sample_path = fuzzerConfig.path_to_mutation_sample + fuzzerConfig.source_input_sample
    num_sample = raw_input("Provide the number of Samples to be Generated : ")
    extension = os.path.splitext(sample_path)[1]
    radamsa_do(sample_path,extension,num_sample)