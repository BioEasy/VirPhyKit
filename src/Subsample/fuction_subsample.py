import random
import os
import argparse
import sys
import re
from collections import OrderedDict

def run_subsampling(fasta_file, num_seqs, region=None, output_dir=None, equal_sampling=False, status_update=None, output_file_name="extract.fas"):
    dict_fas = OrderedDict()

    try:
        with open(fasta_file) as f2:
            line = f2.readline()
            while line != "":
                while not line.startswith('>') and line != "":
                    line = f2.readline()
                fas_name = line.strip()
                fas_seq = ""
                line = f2.readline()
                while not line.startswith('>') and line != "":
                    fas_seq += re.sub(r"\s", "", line)
                    line = f2.readline()
                dict_fas[fas_name] = fas_seq
    except Exception as e:
        raise Exception(f"Error reading FASTA file: {str(e)}")


    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(__file__))
    extract_file = os.path.join(output_dir, output_file_name)

    if equal_sampling:

        site_dict = OrderedDict() 
        for fas_name, fas_seq in dict_fas.items():
   
            match = re.search(r"(?:^|>|_)([A-Za-z0-9]+)(?:_|$)", fas_name)
            if not match:
                raise ValueError(f"Cannot parse site from sequence name: {fas_name}")
            site = match.group(1)
            site_dict.setdefault(site, []).append((fas_name, fas_seq))


        region_counts = {site: len(seqs) for site, seqs in site_dict.items()}

        min_seq_num = min(len(seqs) for seqs in site_dict.values())
        if min_seq_num == 0:
            raise ValueError("Some sites have zero sequences.")

        sample_num = min_seq_num

        sampled_sequences = []
        for site, seqs in site_dict.items():
            sampled = random.sample(seqs, sample_num)
            sampled_sequences.extend(sampled)

        extract_fas = "\n".join([f"{name}\n{seq}" for name, seq in sampled_sequences])
        try:
            with open(extract_file, "w") as f:
                f.write(extract_fas)
        except Exception as e:
            raise Exception(f"Error writing output file {extract_file}: {str(e)}")

    elif region:

        region_sequences = {name: seq for name, seq in dict_fas.items() if region in name}
        remaining_sequences = {name: seq for name, seq in dict_fas.items() if region not in name}
        total_region_sequences = len(region_sequences)

        if num_seqs > total_region_sequences:
            raise ValueError(
                f"Requested to remove {num_seqs} sequences, but only {total_region_sequences} sequences with region {region} are available."
            )

        if num_seqs == total_region_sequences:
            raise ValueError("Cannot remove all sequences, please backup the original file.")

        sequences_to_remove = random.sample(list(region_sequences.items()), num_seqs)
        final_remaining = {
            **remaining_sequences,
            **{name: seq for name, seq in dict_fas.items() if name not in [s[0] for s in sequences_to_remove]}
        }

        extract_fas = "\n".join([f"{name}\n{seq}" for name, seq in sequences_to_remove])
        try:
            with open(extract_file, "w") as f:
                f.write(extract_fas)
        except Exception as e:
            raise Exception(f"Error writing extract file {extract_file}: {str(e)}")

        remaining_fas = "\n".join([f"{name}\n{seq}" for name, seq in final_remaining.items()])
        try:
            with open(fasta_file, "w") as f:
                f.write(remaining_fas)
            return f"<b><span style='color: green;'>Done! Subsampled {num_seqs} sequences from '{region}'. Subsampled sequences saved in {extract_file}, remaining sequences saved in {fasta_file}</span></b>"
        except Exception as e:
            raise Exception(f"Error writing to original file: {str(e)}")
    else:

        total_sequences = len(dict_fas)
        if num_seqs > total_sequences:
            raise ValueError(f"Requested {num_seqs} sequences, but only {total_sequences} available.")

        sampled_sequences = random.sample(list(dict_fas.items()), num_seqs)
        extract_fas = "\n".join([f"{name}\n{seq}" for name, seq in sampled_sequences])
        try:
            with open(extract_file, "w") as f:
                f.write(extract_fas)
        except Exception as e:
            raise Exception(f"Error writing output file {extract_file}: {str(e)}")

        return f"<b><span style='color: green;'>Done! Selected {num_seqs} sequences. Output file: {extract_file}</span></b>"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        prog='function_subsample.py',
        description='Randomly subsample or remove sequences from a FASTA file.',
        epilog=r'''
        1) Randomly select n sequences:
        python function_subsample.py fas_file 100

        2) Meio
        python function_subsample.py fas_file 100 -i _China_
        '''
    )
    parser.add_argument("file", help='input FASTA file')
    parser.add_argument('num_seqs', help='number of sequences to select/remove', type=int)
    parser.add_argument('-i', '--region', help='geographic region to filter (e.g., "China")', default=None)
    myargs = parser.parse_args(sys.argv[1:])
    run_subsampling(myargs.file, myargs.num_seqs, myargs.region, None)