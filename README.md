# PCIE_SETUP - PCIe device configuration utility
The utility is designed for PCIe device configuring and to ease debugging and troubleshooting in Unix-like OS.

It provides facilities for:
  - **speed change** mechanism
  - configuring **max payload size**
  - configuring **max read request size**
  - manual **register field write/read**

## How to use
- Download [latest version from Releases page](https://github.com/raf-stamb/pcie_setup).
- Make sure Python3 installed.
- Make *pcie_setup.py* file executable with `chmod +x ./pcie_setup.py`
- run `./pcie_setup.py`


## How does it work
The utility uses Unix-like commands *setpci* and *lspci* from the *libpci* library.

Supported registers so far are listed in [*reg_list.py*](https://github.com/raf-stamb/pcie_setup/blob/main/regs_list.py):
- *COMMAND*
- *STATUS*
- *DEV_CAP*
- *DEV_CTRL*
- *DEV_STAT*
- *LINK_CAP*
- *LINK_CTRL*
- *LINK_STATUS*
- *SLOT_CAP*
- *SLOT_CTRL*
- *SLOT_STATUS*
- *DEV_CTRL2*
- *DEV_STAT2*
- *LINK_CTRL2*
- *LINK_STATUS2*
- *ROOT_CTRL*
- *ROOT_CAP*
- *ROOT_STATUS*
- *PM_CAP*
- *PM_CSR*
- *PM_CSR_BSE_DATA*
- *MSI_MSG_CTRL*
- *MSIX_MSG_CTRL*
- *MSIX_TBL_OFFSET*
- *MSIX_PBA_OFFSET*
