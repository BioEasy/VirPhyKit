1. **Introduction**

VirPhyKit is designed to simplify the processing of viral sequence data for phylogeographic analysis, offering an efficient alternative to more laborious manual methods. This toolkit integrates 12 specialized modules within an intuitive point-and-click interface, streamlining key tasks such as sequence curation, spatiotemporal subsampling, migration pattern analysis, and molecular dating.

2. **System requirements**

- **Python 3.6 or later**
- **R 3.5 or later**
- **Perl**

Prior to using VirPhyKit, users must specify the installation paths for R, Python, and Perl in the “Options > Environment Settings” menu and click “Check”. The toolkit will then automatically:

- Verify required Python and R package dependencies
- Identify any missing packages
- Prompt users with options to automatically install missing dependencies (on Linux, missing packages must be installed manually).

3. **Installation**

- For Windows, Windows 7, 8, and 10 are all supported. Just download VirPhyKit.zip, unzip it, and then double-click it to run it.
- For Linux, unzip VirPhyKit.zip/VirPhyKit.tar.gz to any path you specify, then double-click VirPhyKit to open it. Or use the command:

  cd path/to/VirPhyKit

  ./VirPhyKit.sh

- If you encounter any permission-related errors, please try using the following command:

  sudo chmod +x VirPhyKit.sh

This will grant the VirPhyKit script execution permissions.

- Note: Both 32-bit and 64-bit of Windows (7 and above) are supported, but only 64-bit has been tested on Linux (Ubuntu).

4. **Quick Guide and Tutorial**

The Quick Guide (Quick_Guide.pdf) provides an overview of the 12 modules in VirPhyKit. For in-depth guidance, a comprehensive Tutorial (Tutorial.pdf) offers step-by-step instructions for the toolkit’s features.

5. **Tools menu in VirPhyKit**

| **Menu**   | **Module/Item** | **Note** |
|------------|-----------------|----------|
| Sample     |                 |          |
|            | SeqHarvester    | Sequence Metadata Harvester |
|            | SeqIDRenamer    | Sequence Identifier Renamer |
|            | SeqGrouper      | Sequence Grouping Tool |
|            | VirSpaceTime    | Viral Space-Time Visualizer |
| Analysis   |                 |          |
|            | RRT             | Region-Randomization Test |
|            | TempMig         | Temporal Migration Tracker |
|            | GeoSubsampler   | Sequence Geographic Subsampler |
| Plot       | BSP-Viz<br>RSPP-Viz | Bayesian Skyline Plot Visualizer<br>Root State Posterior Probability Visualizer |
| Dating     | TreeTime-RTT<br>TreeDater-LTT | Root-to-tip Regression by TreeTime<br>Lineage-Through-Time with Treedater |
| Options    |                 |          |
|            | Environment     | Check the dependency environment |
| Misc       | MJRM Generator  | Markov Jumps and Rewards Matrix Generator |
| Help       | About           | About VirPhyKit |
|            | Quick guide     | Quick guide for new user |
|            | Tutorial        | Tutorial for the user |


6. **Citation**

Yin Y., Shen J., Du Z., Ho S.Y.W., Gao F., 2025. VirPhyKit: an integrated toolkit for viral phylogeographic analysis.

7. **Contribution**

We welcome bug reports, feedback, and suggestions. Please report errors and questions on GitHub Issues. Any contribution via Pull requests will be appreciated.

8. **License** **and Disclaimer**

This project is licensed under the GNU General Public License v3.0 - see the license file \[LICENSE\](LICENSE) for details.

This program is provided without any warranty. No warranty is given as to the functionality of the software, nor as to the accuracy of its results, either express or implied. Please check your results carefully.
