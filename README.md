# goodluck

## Installation
`pip install git+https://github.com/Rhyssiyan/goodluck.git`


## 如果你想将语言设置恢复为英文
`locale-gen 'en_US.UTF-8'`
`update-locale LC_ALL='en_US.UTF-8'`


## Usage

1. Run a program on node satisfying some requirements

* 找到一个空闲的TitanV节点,在其上运行nvidia-smi ``goodluck run "nvidia-smi" --ngpu 1 --card 'v'`` 

Common parameters:
* ngpu: how much gpu you want to use
* env: The environment you want to source(default is conda environment)
* virt_env: if true, source virtual environment
* card: gpu card type. Legal values:'all' | '1080' | 'm40' | 'xp' | 'v' | 'k40' | 'v100' | 'p40'
* exit: If program ends, exit from corresponding node

2. Run multiprogram according to some config

3. Observe what nodes are free in AI cluster

* See all free nodes: ``goodluck watch``
* See free nodes with TITAN V: ``goodluck watch --card 'v'``
* Watch all nodes except the nodes with k series card. 
``watch -c -n 0.1 "goodluck watch --noicon --card 'all,-k' " ``
4. Observe what nodes are free in P40 Cluster
``goodluck p40_watch``
5. Wrap your program with tmux 
* Only wrap with tmux ``goodluck wrap``
* Wrap your command ``goodluck wrap 'nvidia-smi' --env xxx``


## Caution:
* 不要在你的command中再指定显卡, i.e. CUDA_VISIBLE_DEVICES=xx
