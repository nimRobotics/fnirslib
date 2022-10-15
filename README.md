# fnirslib

Library to process and analyze fnirs data

author @nimrobotics [![](https://img.shields.io/twitter/follow/nimrobotics.svg?style=social)](https://twitter.com/intent/follow?screen_name=nimrobotics)


## Installation


```bash
git clone https://github.com/nimRobotics/fnirslib
pip install ./fnirslib
cd fnirslib
pip install -r requirements.txt
```

Uninstall: `pip uninstall fnirslib`

## Usage

See the [examples](examples) directory for usage examples.

## License

MIT License

## Pipeline

```mermaid
  flowchart
    A[raw data <br/> n,3,46]-->C[load_nirs];
    C -->B
    b2 --> D[activation <br/> 3,46];
    D-->E[meanAct]
    b3 --> Y
    Y -->G[connectivity];
    G --> H[effective];
    G --> I[functional];
    E --> Y;
    E --> E1[meanActPlot]
    Y --> E2[meanActStats]
    F[peakAct];
    D-->F
    F-->Y
    Y-->F1[peakActStats]
    F-->F2[peakActPlot]

    subgraph B[get_ROI n,3,46,10]
        b1[aggMethods] --> b2[mean <br/> n,3,46]
        b1 --> b3[concatenate <br/> n,3,46];
        b1 --> b4[list of trials <br/> n,3,46,10]
    end

    b4 --> X
    X -->F

    subgraph X[peak activation]
        x1
    end

    Y[cluster channels mean <br/> n,3,11]
```
