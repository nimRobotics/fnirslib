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
  flowchart TB
    A[raw data]-->B;
    B --> D[activation];
    B --> G[connectivity];
    G --> H[effective];
    G --> I[effective];
    D --> E[mean];
    D --> F[peak];

    subgraph B[aggregrate data]
        a1 --> a2;
    end
```
