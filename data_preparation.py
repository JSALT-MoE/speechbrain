"""
-----------------------------------------------------------------------------
 data_preparation.py

 Description: This library gathers classes form data preparation.
 -----------------------------------------------------------------------------
 """

import os
import errno
from utils import (
    check_opts,
    get_all_files,
    logger_write,
    check_inputs,
    run_shell,
)
from data_io import (
    read_wav_soundfile,
    load_pkl,
    save_pkl,
    read_kaldi_lab,
    write_txt_file,
)


class copy_data_locally:
    """
     -------------------------------------------------------------------------
     data_preparation.copy_data_locally (author: Mirco Ravanelli)

     Description: This class copies a compressed dataset into another folder.
                  It can be used to store the data locally when the original
                  dataset it is stored in a shared filesystem.

     Input (init):  - config (type, dict, mandatory):
                       it is a dictionary containing the keys described below.

                           - data_file (type: file_list, mandatory):
                               it is a list containing the files to copy.

                           - local_folder (type:directory,mandatory):
                               it the local directory where to store the
                               dataset. The dataset will be uncompressed in
                               this folder.

                           - copy_cmd (type: str, optional, default: 'rsync'):
                               it is command to run for copying the dataset.

                           - copy_opts (type: str,optional, default: ''):
                               it is a string containing the flags to be used
                               for the copy command copy_cmd.

                           - uncompress_cmd (type: str, optional,
                            default: 'tar'):
                               it is command to uncompress the dataset.

                           - uncompress_opts (type:str,optional,
                             default: '-zxf'):
                               it is a string containing the flags to be used
                               for the uncompress command.

                   - funct_name (type, str, optional, default: None):
                       it is a string containing the name of the parent
                       function that has called this method.

                   - global_config (type, dict, optional, default: None):
                       it a dictionary containing the global variables of the
                       parent config file.

                   - logger (type, logger, optional, default: None):
                       it the logger used to write debug and error messages.
                       If logger=None and root_cfg=True, the file is created
                       from scratch.

                   - first_input (type, list, optional, default: None)
                      this variable allows users to analyze the first input
                      given when calling the class for the first time.


     Input (call): - inp_lst(type, list, mandatory):
                       by default the input arguments are passed with a list.
                       In this case, the list is empty. The call function is
                       just a dummy function here because all the meaningful
                       computation must be executed only once and they are
                       thus done in the initialization method only.


     Output (call):  - stop_at_lst (type: list):
                       when stop_at is set, it returns the stop_at in a list.
                       Otherwise it returns None. It this case it returns
                       always None.

     Example:    from data_preparation import copy_data_locally

                 data_file='/home/mirco/datasets/TIMIT.tar.gz'
                 local_folder='/home/mirco/datasets/local_folder/TIMIT'

                 # Definition of the config dictionary
                 config={'class_name':'data_processing.copy_data_locally', \
                              'data_file': data_file, \
                              'local_folder':local_folder}

                # Initialization of the class
                copy_data_locally(config)

     -------------------------------------------------------------------------
     """
    def __init__(
        self,
        config,
        funct_name=None,
        global_config=None,
        logger=None,
        first_input=None,
    ):

        # Setting the logger
        self.logger = logger

        # Definition of the expected options
        self.expected_options = {
            "class_name": ("str", "mandatory"),
            "data_file": ("file_list", "mandatory"),
            "local_folder": ("str", "mandatory"),
            "copy_cmd": ("str", "optional", "rsync"),
            "copy_opts": ("str", "optional", ""),
            "uncompress_cmd": ("str", "optional", "tar"),
            "uncompress_opts": ("str", "optional", "-zxf"),
        }

        # Check, cast , and expand the options
        self.conf = check_opts(
            self, self.expected_options, config, logger=self.logger
        )

        # Expected inputs when calling the class (no inputs in this case)
        self.expected_inputs = []

        # Checking the first input
        check_inputs(
            self.conf, self.expected_inputs, first_input, logger=self.logger
        )

        # Try to make the local folder
        try:
            os.makedirs(self.local_folder)
        except OSError as e:
            if e.errno != errno.EEXIST:

                err_msg = "Cannot create the data local folder %s!" % (
                    self.local_folder
                )

                logger_write(err_msg, logfile=self.logger)

        self.local_folder = self.local_folder + "/"
        upper_folder = os.path.dirname(os.path.dirname(self.local_folder))

        # Copying all the files in the data_file list
        for data_file in self.data_file:

            # Destination file
            self.dest_file = upper_folder + "/" + os.path.basename(data_file)

            if not os.path.exists(self.dest_file):

                # Copy data file in the local_folder
                msg = "\tcopying file %s into %s !" % (
                    data_file,
                    self.dest_file,
                )

                logger_write(msg, logfile=self.logger, level="debug")

                cmd = (
                    self.copy_cmd
                    + " "
                    + self.copy_opts
                    + data_file
                    + " "
                    + self.dest_file
                )

                run_shell(cmd)

                # Uncompress the data_file in the local_folder
                msg = "\tuncompressing file %s into %s !" % (
                    self.dest_file,
                    self.local_folder,
                )

                logger_write(msg, logfile=self.logger, level="debug")

                cmd = (
                    self.uncompress_cmd
                    + " "
                    + self.uncompress_opts
                    + self.dest_file
                    + " -C "
                    + " "
                    + self.local_folder
                    + " --strip-components=1"
                )

                run_shell(cmd)

    def __call__(self, inp):
        return


class timit_prepare:
    """
     -------------------------------------------------------------------------
     data_preparation.timit_prepare (author: Mirco Ravanelli)

     Description: This class prepares the scp files for the TIMIT dataset.

     Input (init):  - config (type, dict, mandatory):
                       it is a dictionary containing the keys described below.

                           - data_folder (type: directory, mandatory):
                               it the folder where the original TIMIT dataset
                               is stored.

                           - splits ('train','dev','test',mandatory):
                               it the local directory where to store the
                               dataset. The dataset will be uncompressed in
                               this folder.

                           - kaldi_ali_tr (type: direcory, optional,
                               default: 'None'):
                               When set, this is the directiory where the
                               kaldi training alignments are stored.
                               They will be automatically converted into pkl
                               for an easier use within speechbrain.

                           - kaldi_ali_dev (type: direcory, optional,
                               default: 'None'):
                               When set, this is the directiory where the
                               kaldi dev alignments are stored.

                           - kaldi_ali_te (type: direcory, optional,
                               default: 'None'):
                               When set, this is the directiory where the
                               kaldi test alignments are stored.

                           - save_folder (type: str,optional, default: None):
                               it the folder where to store the scp files.
                               If None, the results will be saved in
                               $output_folder/prepare_timit/*.scp.

                   - funct_name (type, str, optional, default: None):
                       it is a string containing the name of the parent
                       function that has called this method.

                   - global_config (type, dict, optional, default: None):
                       it a dictionary containing the global variables of the
                       parent config file.

                   - logger (type, logger, optional, default: None):
                       it the logger used to write debug and error messages.
                       If logger=None and root_cfg=True, the file is created
                       from scratch.

                   - first_input (type, list, optional, default: None)
                      this variable allows users to analyze the first input
                      given when calling the class for the first time.


     Input (call): - inp_lst(type, list, mandatory):
                       by default the input arguments are passed with a list.
                       In this case, the list is empty. The call function is
                       just a dummy function here because all the meaningful
                       computation must be executed only once and they are
                       thus done in the initialization method only.


     Output (call):  - stop_at_lst (type: list):
                       when stop_at is set, it returns the stop_at in a list.
                       Otherwise it returns None. It this case it returns
                       always None.

     Example:    from data_preparation import timit_prepare

                 local_folder='/home/mirco/datasets/TIMIT'
                 save_folder='exp/TIMIT_exp'

                 # Definition of the config dictionary
                 config={'class_name':'data_processing.copy_data_locally', \
                              'data_folder': local_folder, \
                              'splits':'train,test,dev',
                               'save_folder': save_folder}

                # Initialization of the class
                timit_prepare(config)

     -------------------------------------------------------------------------
     """

    def __init__(
        self,
        config,
        funct_name=None,
        global_config=None,
        logger=None,
        first_input=None,
    ):

        self.logger = logger

        # Here are summarized the expected options for this class
        self.expected_options = {
            "class_name": ("str", "mandatory"),
            "data_folder": ("directory", "mandatory"),
            "splits": ("one_of_list(train,dev,test)", "mandatory"),
            "kaldi_ali_tr": ("directory", "optional", "None"),
            "kaldi_ali_dev": ("directory", "optional", "None"),
            "kaldi_ali_test": ("directory", "optional", "None"),
            "kaldi_lab_opts": ("str", "optional", "None"),
            "save_folder": ("str", "optional", "None"),
        }

        # Check, cast , and expand the options
        self.conf = check_opts(
            self, self.expected_options, config, logger=self.logger
        )

        # Expected inputs when calling the class (no inputs in this case)
        self.expected_inputs = []

        # Check the first input
        check_inputs(
            self.conf, self.expected_inputs, first_input, logger=self.logger
        )

        # Other variables
        self.global_config = global_config
        self.samplerate = 16000

        # List of test speakers
        self.test_spk = [
            "fdhc0",
            "felc0",
            "fjlm0",
            "fmgd0",
            "fmld0",
            "fnlp0",
            "fpas0",
            "fpkt0",
            "mbpm0",
            "mcmj0",
            "mdab0",
            "mgrt0",
            "mjdh0",
            "mjln0",
            "mjmp0",
            "mklt0",
            "mlll0",
            "mlnt0",
            "mnjm0",
            "mpam0",
            "mtas1",
            "mtls0",
            "mwbt0",
            "mwew0",
        ]

        # List of dev speakers
        self.dev_spk = [
            "fadg0",
            "faks0",
            "fcal1",
            "fcmh0",
            "fdac1",
            "fdms0",
            "fdrw0",
            "fedw0",
            "fgjd0",
            "fjem0",
            "fjmg0",
            "fjsj0",
            "fkms0",
            "fmah0",
            "fmml0",
            "fnmr0",
            "frew0",
            "fsem0",
            "majc0",
            "mbdg0",
            "mbns0",
            "mbwm0",
            "mcsh0",
            "mdlf0",
            "mdls0",
            "mdvc0",
            "mers0",
            "mgjf0",
            "mglb0",
            "mgwt0",
            "mjar0",
            "mjfc0",
            "mjsw0",
            "mmdb1",
            "mmdm2",
            "mmjr0",
            "mmwh0",
            "mpdf0",
            "mrcs0",
            "mreb0",
            "mrjm4",
            "mrjr0",
            "mroa0",
            "mrtk0",
            "mrws1",
            "mtaa0",
            "mtdt0",
            "mteb0",
            "mthc0",
            "mwjg0",
        ]

        # Avoid calibration sentences
        self.avoid_sentences = ["sa1", "sa2"]

        # Setting file extension.
        self.extension = [".wav"]

        # Setting the save folder
        if self.save_folder is None:
            self.output_folder = self.global_config["output_folder"]
            self.save_folder = self.output_folder + "/" + funct_name

        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)

        # Setting ouput files
        self.save_opt = self.save_folder + "/opt_timit_prepare.pkl"
        self.save_scp_train = self.save_folder + "/train.scp"
        self.save_scp_dev = self.save_folder + "/dev.scp"
        self.save_scp_test = self.save_folder + "/test.scp"

        # Check if this phase is already done (if so, skip it)
        if self.skip():

            msg = "\t%s sucessfully created!" % (self.save_scp_train)
            logger_write(msg, logfile=self.logger, level="debug")

            msg = "\t%s sucessfully created!" % (self.save_scp_dev)
            logger_write(msg, logfile=self.logger, level="debug")

            msg = "\t%s sucessfully created!" % (self.save_scp_test)
            logger_write(msg, logfile=self.logger, level="debug")

            return

        # Additional checks to make sure the data folder contains TIMIT
        self.check_timit_folders()

        msg = "\tCreating scp file for the TIMIT Dataset.."
        logger_write(msg, logfile=self.logger, level="debug")

        # Creating scp file for training data
        if "train" in self.splits:
            match_lst = self.extension + ["train"]

            wav_lst_train = get_all_files(
                self.data_folder,
                match_and=match_lst,
                exclude_or=self.avoid_sentences,
            )

            self.create_scp(
                wav_lst_train,
                self.save_scp_train,
                kaldi_lab=self.kaldi_ali_tr,
                kaldi_lab_opts=self.kaldi_lab_opts,
                logfile=self.logger,
            )

        # Creating scp file for dev data
        if "dev" in self.splits:
            match_lst = self.extension + ["test"]

            wav_lst_dev = get_all_files(
                self.data_folder,
                match_and=match_lst,
                match_or=self.dev_spk,
                exclude_or=self.avoid_sentences,
            )

            self.create_scp(
                wav_lst_dev,
                self.save_scp_dev,
                kaldi_lab=self.kaldi_ali_dev,
                kaldi_lab_opts=self.kaldi_lab_opts,
                logfile=self.logger,
            )

        # Creating scp file for test data
        if "test" in self.splits:
            match_lst = self.extension + ["test"]

            wav_lst_test = get_all_files(
                self.data_folder,
                match_and=match_lst,
                match_or=self.test_spk,
                exclude_or=self.avoid_sentences,
            )

            self.create_scp(
                wav_lst_test,
                self.save_scp_test,
                kaldi_lab=self.kaldi_ali_test,
                kaldi_lab_opts=self.kaldi_lab_opts,
                logfile=self.logger,
            )

        # Saving options (useful to skip this phase when already done)
        save_pkl(self.conf, self.save_opt)

    def __call__(self, inp):
        return []

    def skip(self):
        """
         ---------------------------------------------------------------------
         data_preparation.prepare_timit.skip (author: Mirco Ravanelli)

         Description: This function detects when the timit data_preparation
                      has been already done and can be skipped.

         Input:        - self (type, prepare_timit class, mandatory)


         Output:      - skip (type: boolean):
                           if True, the preparation phase can be skipped.
                           if False, it must be done.

         Example:    from data_preparation import timit_prepare

                     local_folder='/home/mirco/datasets/TIMIT'
                     save_folder='exp/TIMIT_exp'

                     # Definition of the config dictionary
                     config={'class_name':\
                            'data_processing.copy_data_locally',\
                            'data_folder': local_folder, \
                            'splits':'train,test,dev',
                            'save_folder': save_folder}

                    # Initialization of the class
                    data_prep=timit_prepare(config)

                   # Skip function is True because data_pre has already
                   been done:
                   print(data_prep.skip())

         ---------------------------------------------------------------------
         """

        # Checking folders and save options
        skip = False

        if (
            os.path.isfile(self.save_scp_train)
            and os.path.isfile(self.save_scp_dev)
            and os.path.isfile(self.save_scp_test)
            and os.path.isfile(self.save_opt)
        ):
            opts_old = load_pkl(self.save_opt)
            if opts_old == self.conf:
                skip = True

        return skip

    def create_scp(
        self,
        wav_lst,
        scp_file,
        kaldi_lab=None,
        kaldi_lab_opts=None,
        logfile=None,
    ):
        """
         ---------------------------------------------------------------------
         data_preparation.prepare_timit.create_scp (author: Mirco Ravanelli)

         Description: This function creates the scp file given a list of wav
                       files.

         Input:        - self (type, prepare_timit class, mandatory)

                       - wav_lst (type: list, mandatory):
                           it is the list of wav files of a given data split.

                       - scp_file (type:file, mandatory):
                           it is the path of the output scp file

                       - kaldi_lab (type:file, optional, default:None):
                           it is the path of the kaldi labels (optional).

                       - kaldi_lab_opts (type:str, optional, default:None):
                           it a string containing the options use to compute
                           the labels.

                       - logfile(type, logger, optional, default: None):
                           it the logger used to write debug and error msgs.


         Output:      None


         Example:   from data_preparation import timit_prepare

                    local_folder='/home/mirco/datasets/TIMIT'
                    save_folder='exp/TIMIT_exp'

                    # Definition of the config dictionary
                    config={'class_name':'data_processing.copy_data_locally',\
                                  'data_folder': local_folder, \
                                  'splits':'train,test,dev',
                                   'save_folder': save_folder}

                   # Initialization of the class
                   data_prep=timit_prepare(config)

                   # Get scp list
                   wav_lst=['/home/mirco/datasets/TIMIT\
                           /train/dr3/mtpg0/sx213.wav',
                           '/home/mirco/datasets/TIMIT\
                           /train/dr3/mtpg0/si2013.wav']

                   scp_file='exp/ex_scp.scp'
                   data_prep.create_scp(wav_lst,scp_file)

         ---------------------------------------------------------------------
         """

        # Adding some Prints
        msg = '\t"Creating scp lists in  %s..."' % (scp_file)
        logger_write(msg, logfile=self.logger, level="debug")

        # Reading kaldi labels if needed:
        snt_no_lab = 0
        missing_lab = False

        if kaldi_lab is not None:

            lab = read_kaldi_lab(
                kaldi_lab,
                kaldi_lab_opts,
                logfile=self.global_config["output_folder"] + "/log.log",
            )

            lab_out_dir = self.save_folder + "/kaldi_labels"

            if not os.path.exists(lab_out_dir):
                os.makedirs(lab_out_dir)

        scp_lines = []

        # Processing all the wav files in the list
        for wav_file in wav_lst:

            # Getting sentence and speaker ids
            spk_id = wav_file.split("/")[-2]
            snt_id = wav_file.split("/")[-1].replace(".wav", "")

            snt_id = spk_id + "_" + snt_id

            if kaldi_lab is not None:
                if snt_id not in lab.keys():
                    missing_lab = False

                    msg = (
                         '\tThe sentence %s does not have a corresponding '
                         'kaldi label' % (snt_id)
                    )

                    logger_write(msg, logfile=self.logger, level="debug")

                    snt_no_lab = snt_no_lab + 1
                else:
                    snt_lab_path = lab_out_dir + "/" + snt_id + ".pkl"
                    save_pkl(lab[snt_id], snt_lab_path)

                # If too many kaldi labels are missing rise an error
                if snt_no_lab / len(wav_lst) > 0.05:

                    err_msg = (
                        'Too many sentences do not have the '
                        'corresponding kaldi label. Please check data and '
                        'kaldi labels (check %s and %s).'
                        % (self.data_folder, self.kaldi_ali_test)
                    )

                    logger_write(err_msg, logfile=self.logger)

            if missing_lab:
                continue

            # Reading the signal (to retrieve duration in seconds)
            signal = read_wav_soundfile(wav_file, logger=logfile)
            duration = signal.shape[0] / self.samplerate

            # Retrieving words
            wrd_file = wav_file.replace(".wav", ".wrd")
            if not os.path.exists(os.path.dirname(wrd_file)):

                err_msg = "the wrd file %s does not exists!" % (wrd_file)

                logger_write(err_msg, logfile=logfile)

            words = [
                line.rstrip("\n").split(" ")[2] for line in open(wrd_file)
            ]

            words = "_".join(words)

            # Retrieving phonemes
            phn_file = wav_file.replace(".wav", ".phn")

            if not os.path.exists(os.path.dirname(phn_file)):

                err_msg = "the wrd file %s does not exists!" % (phn_file)

                logger_write(err_msg, logfile=logfile)

            phonemes = [
                line.rstrip("\n").replace("h#", "sil").split(" ")[2]
                for line in open(phn_file)
            ]

            phonemes = "_".join(phonemes)

            # Composition of the scp_line
            scp_line = (
                "ID="
                + snt_id
                + " duration="
                + str(duration)
                + " wav=("
                + wav_file
                + ",wav)"
                + " spk_id=("
                + spk_id
                + ",string)"
                + " phn=("
                + str(phonemes).replace(" ", "_")
                + ",string)"
                + " wrd=("
                + str(words).replace(" ", "_")
                + ",string)"
            )

            if kaldi_lab is not None:
                scp_line = scp_line + " kaldi_lab=(" + snt_lab_path + ",pkl)"

            # Adding this line to the scp_lines list
            scp_lines.append(scp_line)

        # -Writing the scp lines
        write_txt_file(scp_lines, scp_file, logger=self.logger)

        # Final prints
        msg = "\t%s sucessfully created!" % (scp_file)
        logger_write(msg, logfile=self.logger, level="debug")

    def check_timit_folders(self):
        """
         ---------------------------------------------------------------------
         data_preparation.check_timit_folders (author: Mirco Ravanelli)

         Description: This function cheks if the dat folder actually contains
                      the TIMIT dataset. If not, it raises an error.

         Input:        - self (type, prepare_timit class, mandatory)


         Output:      None


         Example:   from data_preparation import timit_prepare

                    local_folder='/home/mirco/datasets/TIMIT'
                    save_folder='exp/TIMIT_exp'

                    # Definition of the config dictionary
                    config={'class_name':'data_processing.copy_data_locally',\
                                  'data_folder': local_folder, \
                                  'splits':'train,test,dev',
                                   'save_folder': save_folder}

                   # Initialization of the class
                   data_prep=timit_prepare(config)

                   # Check folder
                   data_prep.check_timit_folders()

         ---------------------------------------------------------------------
         """

        # Checking test/dr1
        if not os.path.exists(self.data_folder + "/test/dr1"):

            err_msg = (
                'the folder %s does not exist (it is expected in '
                'the TIMIT dataset)'
                % (self.data_folder + "/test/dr*")
            )

            logger_write(err_msg, logfile=self.logger)

        # Checking train/dr1
        if not os.path.exists(self.data_folder + "/train/dr1"):

            err_msg = (
                'the folder %s does not exist (it is expected in '
                'the TIMIT dataset)'
                % (self.data_folder + "/train/dr*")
            )

            logger_write(err_msg, logfile=self.logger)


class librispeech_prepare:
    """
     -------------------------------------------------------------------------
     data_preparation.librispeech_prepare (author: Mirco Ravanelli)

     Description: This class prepares the scp files for the LibriSpeech
                  dataset.

     Input (init):  - config (type, dict, mandatory):
                       it is a dictionary containing the keys described below.

                           - data_folder (type: directory, mandatory):
                               it the folder where the original TIMIT dataset
                               is stored.

                           - splits ('dev-clean','dev-others','test-clean','
                             'test-others','train-clean-100',
                             'train-clean-360', 'train-other-500',mandatory):
                               it contains the list of splits for which we are
                               going to create the corresponding scp file.

                           - select_n_sentences (type:int,opt,
                             default:'None'0):
                               it is the number of sentences to select.
                               It might be useful for debugging when I want to
                               test the script on a reduced number of
                               sentences only.

                           - save_folder (type: str,optional, default: None):
                               it the folder where to store the scp files.
                               If None, the results will be saved in
                               $output_folder/prepare_librispeech/*.scp.

                   - funct_name (type, str, optional, default: None):
                       it is a string containing the name of the parent
                       function that has called this method.

                   - global_config (type, dict, optional, default: None):
                       it a dictionary containing the global variables of the
                       parent config file.

                   - logger (type, logger, optional, default: None):
                       it the logger used to write debug and error messages.
                       If logger=None and root_cfg=True, the file is created
                       from scratch.

                   - first_input (type, list, optional, default: None)
                      this variable allows users to analyze the first input
                      given when calling the class for the first time.


     Input (call): - inp_lst(type, list, mandatory):
                       by default the input arguments are passed with a list.
                       In this case, the list is empty. The call function is
                       just a dummy function here because all the meaningful
                       computation must be executed only once and they are
                       thus done in the initialization method only.


     Output (call):  - stop_at_lst (type: list):
                       when stop_at is set, it returns the stop_at in a list.
                       Otherwise it returns None. It this case it returns
                       always None.

     Example:    from data_preparation import librispeech_prepare

                 local_folder='/home/mirco/datasets/LibriSpeech'
                 save_folder='exp/LibriSpeech_exp'

                 # Definition of the config dictionary
                 config={'class_name':'data_processing.copy_data_locally', \
                              'data_folder': local_folder, \
                              'splits':'dev-clean,test-clean',
                               'save_folder': save_folder}

                # Running the data preparation
                librispeech_prepare(config)

     -------------------------------------------------------------------------
     """

    def __init__(
        self,
        config,
        funct_name=None,
        global_config=None,
        logger=None,
        first_input=None,
    ):

        # Logger setup
        self.logger = logger

        # Here are summarized the expected options for this class
        self.expected_options = {
            "data_folder": ("directory", "mandatory"),
            "splits": (
                "one_of_list(dev-clean,dev-others,test-clean,test-others,\
                                train-clean-100,train-clean-360,\
                                train-other-500)",
                "mandatory",
            ),
            "save_folder": ("str", "optional", "None"),
            "select_n_sentences": ("int_list(1,inf)", "optional", "None"),
        }

        # Check, cast , and expand the options
        self.conf = check_opts(
            self, self.expected_options, config, logger=self.logger
        )

        # Expected input
        self.expected_inputs = []

        # Check the first input
        check_inputs(
            self.conf, self.expected_inputs, first_input, logger=self.logger
        )

        # Other variables
        self.samplerate = 16000
        self.funct_name = funct_name

        # Saving folder
        if self.save_folder is None:
            self.output_folder = global_config["output_folder"]
            self.save_folder = self.output_folder + "/" + funct_name

        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)

        self.save_opt = self.save_folder + "/opt_librispeech_prepare.pkl"

        # Check if this phase is already done (if so, skip it)
        if self.skip():
            for split in self.splits:
                text = self.save_folder + "/" + split + ".scp"
                msg = "\t" + text + " created!"
                logger_write(msg, logfile=self.logger, level="debug")
            return

        # Additional checks to make sure the data folder contains Librispeech
        self.check_librispeech_folders()

        # create scp files for each split
        for split_index in range(len(self.splits)):

            split = self.splits[split_index]

            wav_lst = get_all_files(
                self.data_folder + "/" + split, match_and=[".flac"]
            )

            text_lst = get_all_files(
                self.data_folder + "/" + split, match_and=["trans.txt"]
            )

            text_dict = self.text_to_dict(text_lst)

            if self.select_n_sentences is not None:
                select_n_sentences = self.select_n_sentences[split_index]
            else:
                select_n_sentences = len(wav_lst)

            self.create_scp(wav_lst, text_dict, split, select_n_sentences)

        # saving options
        save_pkl(self.conf, self.save_opt)

    def __call__(self, inp):
        return []

    def create_scp(self, wav_lst, text_dict, split, select_n_sentences):
        """
         ---------------------------------------------------------------------
         data_preparation.prepare_librispeech.create_scp
         (author: Mirco Ravanelli)

         Description: This function creates the scp file given a list of wav
                      files.

         Input:        - self (type, prepare_librispeecg class, mandatory)

                       - wav_lst (type: list, mandatory):
                           it is the list of wav files of a given data split.

                       - text_dict (type: list, mandatory):
                           it is the a dictionary containing the text of each
                           sentence.

                       - split (type: str, mandatory):
                           it is the name of the current data split.

                       - select_n_sentences (type:int,opt, default:'None'0):
                           it is the number of sentences to select.

         Output:      None


         Example:   from data_preparation import librispeech_prepare

                    local_folder='/home/mirco/datasets/LibriSpeech'
                    save_folder='exp/LibriSpeech_exp'

                    # Definition of the config dictionary
                    config={'class_name':'data_processing.copy_data_locally',\
                                  'data_folder': local_folder, \
                                  'splits':'train,test,dev',
                                   'save_folder': save_folder}

                   # Initialization of the class
                   data_prep=librispeech_prepare(config)

                   # Get scp list
                   wav_lst=['/home/mirco/datasets/LibriSpeech/dev-clean/84\
                   /121123/84-121123-0000.flac']

                   text_dict={'84-121123-0000':'Hello world'}

                   split='debug_split'

                   select_n_sentences=1

                   data_prep.create_scp(wav_lst,text_dict,split,
                   select_n_sentences)

                   # take a look into exp/LibriSpeech_exp

         ---------------------------------------------------------------------
         """

        # Setting path for the scp file
        scp_file = self.save_folder + "/" + split + ".scp"

        # Preliminary prints
        msg = "\tCreating scp lists in  %s..." % (scp_file)
        logger_write(msg, logfile=self.logger, level="debug")

        scp_lines = []
        snt_cnt = 0

        # Processing all the wav files in wav_lst
        for wav_file in wav_lst:

            snt_id = wav_file.split("/")[-1].replace(".flac", "")
            spk_id = "-".join(snt_id.split("-")[0:2])
            wrd = text_dict[snt_id]

            signal = read_wav_soundfile(wav_file, logger=self.logger)
            duration = signal.shape[0] / self.samplerate

            # Composing the scp file
            scp_line = (
                "ID="
                + snt_id
                + " duration="
                + str(duration)
                + " wav=("
                + wav_file
                + ",flac)"
                + " spk_id=("
                + spk_id
                + ",string)"
                + " wrd=("
                + wrd
                + ",string)"
            )

            #  Appending current file to the scp_lines list
            scp_lines.append(scp_line)
            snt_cnt = snt_cnt + 1

            if snt_cnt == select_n_sentences:
                break

        # Writing the scp_lines
        write_txt_file(scp_lines, scp_file, logger=self.logger)

        # Final print
        msg = "\t%s sucessfully created!" % (scp_file)
        logger_write(msg, logfile=self.logger, level="debug")

    def skip(self):
        """
         ---------------------------------------------------------------------
         data_preparation.prepare_librispeech.skip (author: Mirco Ravanelli)

         Description: This function detects when the librispeeh data_prep
                       has been already done and can be skipped.

         Input:        - self (type, prepare_timit class, mandatory)


         Output:      - skip (type: boolean):
                           if True, the preparation phase can be skipped.
                           if False, it must be done.

         Example:    from data_preparation import librispeech_prepare

                     local_folder='/home/mirco/datasets/LibriSpeech'
                     save_folder='exp/LibriSpeech_exp'

                     # Definition of the config dictionary
                     config={'class_name':\
                             'data_processing.copy_data_locally', \
                             'data_folder': local_folder, \
                             'splits':'dev-clean,test-clean',
                             'save_folder': save_folder}

                    # Running the data preparation
                    data_prep=librispeech_prepare(config)

                   # Skip function is True because data_pre has already been
                   done:
                   print(data_prep.skip())

         ---------------------------------------------------------------------
         """

        # Checking scp files
        skip = True

        for split in self.splits:
            if not os.path.isfile(self.save_folder + "/" + split + ".scp"):
                skip = False

        #  Checking saved options
        if skip is True:
            if os.path.isfile(self.save_opt):
                opts_old = load_pkl(self.save_opt)
                if opts_old == self.conf:
                    skip = True
                else:
                    skip = False
        return skip

    @staticmethod
    def text_to_dict(text_lst):
        """
         ---------------------------------------------------------------------
         data_preparation.prepare_librispeech.text_to_dict
         (author: Mirco Ravanelli)

         Description: This converts lines of text into a dictionary-

         Input:        - self (type: prepare_timit class, mandatory)

                       text_lst (type: file, mandatory):
                        it is the file containing  the librispeech text
                        transcription.

         Output:      text_dict (type: dictionary)
                           it is the dictionary containing the text
                           transcriptions for each sentence.

         Example:    from data_preparation import librispeech_prepare

                     local_folder='/home/mirco/datasets/LibriSpeech'
                     save_folder='exp/LibriSpeech_exp'

                     # Definition of the config dictionary
                     config={'class_name':
                             'data_processing.copy_data_locally', \
                             'data_folder': local_folder, \
                             'splits':'dev-clean,test-clean',
                             'save_folder': save_folder}

                    # Running the data preparation
                    data_prep=librispeech_prepare(config)

                    # Text dictionary creation
                    text_lst=['/home/mirco/datasets/LibriSpeech/dev-clean\
                    /84/121550/84-121550.trans.txt']

                    print(data_prep.text_to_dict(text_lst))

         ---------------------------------------------------------------------
         """

        # Initialization of the text dictionary
        text_dict = {}

        # Reading all the transcription files is text_lst
        for file in text_lst:
            with open(file, "r") as f:

                # Reading all line of the transcription file
                for line in f:
                    line_lst = line.strip().split(" ")
                    text_dict[line_lst[0]] = "_".join(line_lst[1:])

        return text_dict

    def check_librispeech_folders(self):
        """
         ---------------------------------------------------------------------
         data_preparation.check_librispeech_folders (author: Mirco Ravanelli)

         Description: This function cheks if the dat folder actually contains
                      the LibriSpeech dataset. If not, it raises an error.

         Input:        - self (type, prepare_librispeech class, mandatory)


         Output:      None


         Example:    from data_preparation import librispeech_prepare

                     local_folder='/home/mirco/datasets/LibriSpeech'
                     save_folder='exp/LibriSpeech_exp'

                     # Definition of the config dictionary
                     config={'class_name':
                             'data_processing.copy_data_locally', \
                             'data_folder': local_folder, \
                             'splits':'dev-clean,test-clean',
                              'save_folder': save_folder}

                    # Running the data preparation
                    data_prep=librispeech_prepare(config)

                   # Check folder
                   data_prep.check_librispeech_folders()

         ---------------------------------------------------------------------
         """

        # Checking if all the splits exist
        for split in self.splits:
            if not os.path.exists(self.data_folder + "/" + split):

                err_msg = (
                    'the folder %s does not exist (it is expected in the '
                    'Librispeech dataset)'
                    % (self.data_folder + "/" + split)
                )

                logger_write(err_msg, logfile=self.logger)
