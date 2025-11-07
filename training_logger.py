#!/usr/bin/env python3
"""
Custom callback pour capturer automatiquement les métriques de training
et générer les graphiques à la fin.
"""
import json
import os
from pathlib import Path
from datetime import datetime
from transformers import TrainerCallback, TrainerState, TrainerControl
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


class AutomatedTrainingLogger(TrainerCallback):
    """
    Callback personnalisé pour:
    1. Capturer automatiquement tous les logs de training
    2. Sauvegarder les paramètres de fine-tuning au démarrage
    3. Générer automatiquement les graphiques à la fin
    """

    def __init__(self):
        super().__init__()
        self.logs = []
        self.output_dir = None
        self.start_time = None

    def on_train_begin(self, args, state: TrainerState, control: TrainerControl, **kwargs):
        """Au début du training : sauvegarder les paramètres"""
        self.output_dir = args.output_dir
        self.start_time = datetime.now()

        print(f"\n{'='*70}")
        print(f"🚀 DÉBUT DU FINE-TUNING")
        print(f"{'='*70}")
        print(f"📁 Output dir: {self.output_dir}")
        print(f"🕐 Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Créer le répertoire de sortie s'il n'existe pas
        os.makedirs(self.output_dir, exist_ok=True)

        # Sauvegarder les paramètres de training
        self._save_training_config(args, state, kwargs)

    def on_log(self, args, state: TrainerState, control: TrainerControl, logs=None, **kwargs):
        """À chaque log : capturer les métriques"""
        if logs is None:
            return

        # Capturer uniquement les logs de training (pas les logs d'évaluation)
        if 'loss' in logs and state.global_step > 0:
            log_entry = {
                'step': state.global_step,
                'epoch': state.epoch,
                'loss': logs.get('loss', None),
                'grad_norm': logs.get('grad_norm', None),
                'learning_rate': logs.get('learning_rate', None),
                'entropy': logs.get('entropy', None),
                'num_tokens': logs.get('num_tokens', None),
                'mean_token_accuracy': logs.get('mean_token_accuracy', None),
            }

            # Filtrer les None
            log_entry = {k: v for k, v in log_entry.items() if v is not None}

            self.logs.append(log_entry)

            # Sauvegarder les logs en temps réel
            self._save_logs_realtime()

    def on_train_end(self, args, state: TrainerState, control: TrainerControl, **kwargs):
        """À la fin du training : générer les graphiques et le résumé"""
        end_time = datetime.now()
        duration = end_time - self.start_time

        print(f"\n{'='*70}")
        print(f"✅ FIN DU FINE-TUNING")
        print(f"{'='*70}")
        print(f"🕐 End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Duration: {duration}")
        print(f"📊 Total steps: {len(self.logs)}")

        # Sauvegarder les logs finaux
        self._save_logs_final()

        # Générer les graphiques
        if len(self.logs) > 0:
            print(f"\n📈 Génération des graphiques...")
            self._generate_plots()
            print(f"✅ Graphiques générés dans {self.output_dir}/")

        # Générer le résumé
        self._generate_summary(duration)

    def _save_training_config(self, args, state, kwargs):
        """Sauvegarde les paramètres de training"""
        config_file = os.path.join(self.output_dir, 'training_config.json')

        config = {
            'start_time': self.start_time.isoformat(),
            'training_args': {
                'learning_rate': args.learning_rate,
                'num_train_epochs': args.num_train_epochs,
                'per_device_train_batch_size': args.per_device_train_batch_size,
                'per_device_eval_batch_size': args.per_device_eval_batch_size,
                'gradient_accumulation_steps': args.gradient_accumulation_steps,
                'warmup_ratio': args.warmup_ratio,
                'lr_scheduler_type': args.lr_scheduler_type,
                'max_grad_norm': args.max_grad_norm,
                'weight_decay': args.weight_decay,
                'adam_beta1': args.adam_beta1,
                'adam_beta2': args.adam_beta2,
                'adam_epsilon': args.adam_epsilon,
                'max_seq_length': getattr(args, 'max_seq_length', None),
                'logging_steps': args.logging_steps,
                'eval_strategy': args.eval_strategy,
                'eval_steps': args.eval_steps if hasattr(args, 'eval_steps') else None,
                'save_strategy': args.save_strategy,
                'save_steps': args.save_steps,
                'seed': args.seed,
                'output_dir': args.output_dir,
            },
            'model_config': {
                'model_name': kwargs.get('model', {}).config.name_or_path if 'model' in kwargs and hasattr(kwargs['model'], 'config') else 'unknown',
            }
        }

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"✅ Config sauvegardée: {config_file}")

    def _save_logs_realtime(self):
        """Sauvegarde les logs en temps réel"""
        logs_file = os.path.join(self.output_dir, 'training_logs.jsonl')

        # Écrire uniquement la dernière ligne (append mode)
        with open(logs_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(self.logs[-1], ensure_ascii=False) + '\n')

    def _save_logs_final(self):
        """Sauvegarde finale de tous les logs"""
        # Format JSONL (compatible avec l'ancien format)
        logs_file = os.path.join(self.output_dir, 'training_logs.jsonl')
        with open(logs_file, 'w', encoding='utf-8') as f:
            for log in self.logs:
                f.write(json.dumps(log, ensure_ascii=False) + '\n')

        # Format JSON complet (plus facile à lire)
        logs_json = os.path.join(self.output_dir, 'training_logs.json')
        with open(logs_json, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, indent=2, ensure_ascii=False)

        print(f"✅ Logs sauvegardés: {logs_file}")
        print(f"✅ Logs sauvegardés: {logs_json}")

    def _generate_plots(self):
        """Génère les graphiques de training"""
        # Préparer les données
        data = {
            'step': [],
            'epoch': [],
            'loss': [],
            'grad_norm': [],
            'learning_rate': [],
            'entropy': [],
            'mean_token_accuracy': []
        }

        for log in self.logs:
            for key in data.keys():
                if key in log:
                    data[key].append(log[key])
                elif key == 'step':
                    data[key].append(len(data[key]) + 1)

        # Vérifier qu'il y a des données
        if len(data['loss']) == 0:
            print("⚠️  Pas de données de loss disponibles")
            return

        # 1. Graphique complet avec toutes les métriques
        self._plot_all_metrics(data)

        # 2. Graphique de la loss seule
        self._plot_loss_only(data)

    def _plot_all_metrics(self, data):
        """Graphique complet avec toutes les métriques"""
        fig, axes = plt.subplots(3, 2, figsize=(15, 12))
        fig.suptitle('Métriques de Fine-tuning', fontsize=16, fontweight='bold')

        # 1. Loss vs Step
        if len(data['loss']) > 0:
            axes[0, 0].plot(data['step'], data['loss'], color='#e74c3c', linewidth=1.5, alpha=0.7)
            axes[0, 0].set_xlabel('Step')
            axes[0, 0].set_ylabel('Loss')
            axes[0, 0].set_title('Training Loss')
            axes[0, 0].grid(True, alpha=0.3)

        # 2. Loss vs Epoch
        if len(data['epoch']) > 0 and len(data['loss']) > 0:
            axes[0, 1].plot(data['epoch'], data['loss'], color='#e74c3c', linewidth=1.5, alpha=0.7)
            axes[0, 1].set_xlabel('Epoch')
            axes[0, 1].set_ylabel('Loss')
            axes[0, 1].set_title('Loss par Epoch')
            axes[0, 1].grid(True, alpha=0.3)

        # 3. Learning Rate
        if len(data['learning_rate']) > 0:
            axes[1, 0].plot(data['step'][:len(data['learning_rate'])], data['learning_rate'],
                          color='#3498db', linewidth=1.5, alpha=0.7)
            axes[1, 0].set_xlabel('Step')
            axes[1, 0].set_ylabel('Learning Rate')
            axes[1, 0].set_title('Learning Rate Schedule')
            axes[1, 0].grid(True, alpha=0.3)
            axes[1, 0].ticklabel_format(style='scientific', axis='y', scilimits=(0,0))

        # 4. Token Accuracy
        if len(data['mean_token_accuracy']) > 0:
            axes[1, 1].plot(data['step'][:len(data['mean_token_accuracy'])], data['mean_token_accuracy'],
                          color='#2ecc71', linewidth=1.5, alpha=0.7)
            axes[1, 1].set_xlabel('Step')
            axes[1, 1].set_ylabel('Accuracy')
            axes[1, 1].set_title('Mean Token Accuracy')
            axes[1, 1].grid(True, alpha=0.3)

        # 5. Gradient Norm
        if len(data['grad_norm']) > 0:
            axes[2, 0].plot(data['step'][:len(data['grad_norm'])], data['grad_norm'],
                          color='#f39c12', linewidth=1.5, alpha=0.7)
            axes[2, 0].set_xlabel('Step')
            axes[2, 0].set_ylabel('Gradient Norm')
            axes[2, 0].set_title('Gradient Norm')
            axes[2, 0].grid(True, alpha=0.3)

        # 6. Entropy
        if len(data['entropy']) > 0:
            axes[2, 1].plot(data['step'][:len(data['entropy'])], data['entropy'],
                          color='#9b59b6', linewidth=1.5, alpha=0.7)
            axes[2, 1].set_xlabel('Step')
            axes[2, 1].set_ylabel('Entropy')
            axes[2, 1].set_title('Entropy')
            axes[2, 1].grid(True, alpha=0.3)

        plt.tight_layout()

        output_path = os.path.join(self.output_dir, 'training_metrics.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"  ✓ {output_path}")
        plt.close()

    def _plot_loss_only(self, data):
        """Graphique de la loss seule avec statistiques"""
        if len(data['loss']) == 0:
            return

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(data['step'][:len(data['loss'])], data['loss'],
               color='#e74c3c', linewidth=2, alpha=0.8)
        ax.set_xlabel('Training Step', fontsize=12)
        ax.set_ylabel('Loss', fontsize=12)
        ax.set_title('Training Loss Evolution', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Statistiques
        min_loss = min(data['loss'])
        max_loss = max(data['loss'])
        final_loss = data['loss'][-1]
        initial_loss = data['loss'][0]
        improvement = ((initial_loss - final_loss) / initial_loss * 100)

        stats_text = f"Initial: {initial_loss:.4f}\nMin: {min_loss:.4f}\nFinal: {final_loss:.4f}\nImprovement: {improvement:.1f}%"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
               fontsize=10)

        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'training_loss.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"  ✓ {output_path}")
        plt.close()

    def _generate_summary(self, duration):
        """Génère un résumé textuel du training"""
        summary_file = os.path.join(self.output_dir, 'training_summary.txt')

        if len(self.logs) == 0:
            return

        # Extraire les métriques
        losses = [log['loss'] for log in self.logs if 'loss' in log]
        accuracies = [log['mean_token_accuracy'] for log in self.logs if 'mean_token_accuracy' in log]
        learning_rates = [log['learning_rate'] for log in self.logs if 'learning_rate' in log]

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("RÉSUMÉ DU FINE-TUNING\n")
            f.write("="*70 + "\n\n")

            f.write(f"📅 Début:     {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"📅 Fin:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"⏱️  Durée:     {duration}\n\n")

            f.write(f"📊 MÉTRIQUES\n")
            f.write("-"*70 + "\n")
            f.write(f"Total steps:          {len(self.logs)}\n")

            if len(losses) > 0:
                f.write(f"\nLoss:\n")
                f.write(f"  - Initiale:         {losses[0]:.4f}\n")
                f.write(f"  - Finale:           {losses[-1]:.4f}\n")
                f.write(f"  - Minimale:         {min(losses):.4f}\n")
                f.write(f"  - Maximale:         {max(losses):.4f}\n")
                f.write(f"  - Amélioration:     {((losses[0] - losses[-1]) / losses[0] * 100):.2f}%\n")

            if len(accuracies) > 0:
                f.write(f"\nAccuracy:\n")
                f.write(f"  - Initiale:         {accuracies[0]:.4f}\n")
                f.write(f"  - Finale:           {accuracies[-1]:.4f}\n")
                f.write(f"  - Amélioration:     {((accuracies[-1] - accuracies[0]) / accuracies[0] * 100):.2f}%\n")

            if len(learning_rates) > 0:
                f.write(f"\nLearning Rate:\n")
                f.write(f"  - Maximum:          {max(learning_rates):.2e}\n")
                f.write(f"  - Finale:           {learning_rates[-1]:.2e}\n")

            f.write("\n" + "="*70 + "\n")
            f.write("Fichiers générés:\n")
            f.write("  - training_logs.jsonl      (logs bruts)\n")
            f.write("  - training_logs.json       (logs JSON)\n")
            f.write("  - training_config.json     (paramètres)\n")
            f.write("  - training_metrics.png     (graphiques complets)\n")
            f.write("  - training_loss.png        (graphique loss)\n")
            f.write("  - training_summary.txt     (ce fichier)\n")
            f.write("="*70 + "\n")

        print(f"✅ Résumé sauvegardé: {summary_file}")

        # Afficher aussi à l'écran
        with open(summary_file, 'r') as f:
            print(f"\n{f.read()}")
