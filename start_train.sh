CUDA_VISIBLE_DEVICES=4,5,6,7 python -m torch.distributed.launch --nproc_per_node=4 run_pretraining_new.py \
    --data_dir=dataset/var_bert_all \
    --config_path=prev_trained_model/config_var.json \
    --vocab_path=prev_trained_model/varaint_vocab.txt \
    --output_dir=outputs \
    --model_path=prev_trained_model \
    --file_num=5