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
  graph TD;
      A-->B;
      A-->C;
      B-->D;
      C-->D;
```
```mermaid
    graph TD
        A[Christmas] -->|Get money| B(Go shopping)
        B --> C{Let me think}
        C -->|One| D[Laptop]
        C -->|Two| E[iPhone]
        C -->|Three| F[fa:fa-car Car]
```