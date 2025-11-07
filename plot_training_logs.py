#!/usr/bin/env python3
"""
Script pour visualiser les logs de fine-tuning
"""
import ast
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Pour sauvegarder sans afficher

def parse_log_file(file_path):
    """Parse le fichier de logs et extrait les métriques"""
    data = {
        'step': [],
        'loss': [],
        'grad_norm': [],
        'learning_rate': [],
        'entropy': [],
        'mean_token_accuracy': [],
        'epoch': []
    }

    step_counter = 0
    errors = 0

    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            try:
                # Évaluer la ligne comme un dictionnaire Python
                log_entry = ast.literal_eval(line.strip())

                # Vérifier que toutes les clés nécessaires sont présentes
                required_keys = ['loss', 'grad_norm', 'learning_rate', 'entropy', 'mean_token_accuracy', 'epoch']
                if not all(key in log_entry for key in required_keys):
                    continue

                step_counter += 1
                data['step'].append(step_counter)
                data['loss'].append(log_entry['loss'])
                data['grad_norm'].append(log_entry['grad_norm'])
                data['learning_rate'].append(log_entry['learning_rate'])
                data['entropy'].append(log_entry['entropy'])
                data['mean_token_accuracy'].append(log_entry['mean_token_accuracy'])
                data['epoch'].append(log_entry['epoch'])
            except Exception:
                errors += 1
                continue

    if errors > 0:
        print(f"Note: {errors} lignes ignorées (barres de progression ou lignes invalides)")

    return data

def plot_training_metrics(data, output_dir='./'):
    """Crée des graphiques pour visualiser les métriques d'entraînement"""

    # Créer une figure avec plusieurs subplots
    fig, axes = plt.subplots(3, 2, figsize=(15, 12))
    fig.suptitle('Métriques de Fine-tuning', fontsize=16, fontweight='bold')

    # 1. Loss
    axes[0, 0].plot(data['step'], data['loss'], color='#e74c3c', linewidth=1.5, alpha=0.7)
    axes[0, 0].set_xlabel('Step')
    axes[0, 0].set_ylabel('Loss')
    axes[0, 0].set_title('Training Loss')
    axes[0, 0].grid(True, alpha=0.3)

    # 2. Loss vs Epoch
    axes[0, 1].plot(data['epoch'], data['loss'], color='#e74c3c', linewidth=1.5, alpha=0.7)
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Loss')
    axes[0, 1].set_title('Loss par Epoch')
    axes[0, 1].grid(True, alpha=0.3)

    # 3. Learning Rate
    axes[1, 0].plot(data['step'], data['learning_rate'], color='#3498db', linewidth=1.5, alpha=0.7)
    axes[1, 0].set_xlabel('Step')
    axes[1, 0].set_ylabel('Learning Rate')
    axes[1, 0].set_title('Learning Rate Schedule')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].ticklabel_format(style='scientific', axis='y', scilimits=(0,0))

    # 4. Token Accuracy
    axes[1, 1].plot(data['step'], data['mean_token_accuracy'], color='#2ecc71', linewidth=1.5, alpha=0.7)
    axes[1, 1].set_xlabel('Step')
    axes[1, 1].set_ylabel('Accuracy')
    axes[1, 1].set_title('Mean Token Accuracy')
    axes[1, 1].grid(True, alpha=0.3)

    # 5. Gradient Norm
    axes[2, 0].plot(data['step'], data['grad_norm'], color='#f39c12', linewidth=1.5, alpha=0.7)
    axes[2, 0].set_xlabel('Step')
    axes[2, 0].set_ylabel('Gradient Norm')
    axes[2, 0].set_title('Gradient Norm')
    axes[2, 0].grid(True, alpha=0.3)

    # 6. Entropy
    axes[2, 1].plot(data['step'], data['entropy'], color='#9b59b6', linewidth=1.5, alpha=0.7)
    axes[2, 1].set_xlabel('Step')
    axes[2, 1].set_ylabel('Entropy')
    axes[2, 1].set_title('Entropy')
    axes[2, 1].grid(True, alpha=0.3)

    plt.tight_layout()

    # Sauvegarder la figure
    output_path = f'{output_dir}/training_metrics.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Graphique sauvegardé: {output_path}")
    plt.close()

    # Créer un graphique séparé pour la loss (plus grande)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(data['step'], data['loss'], color='#e74c3c', linewidth=2, alpha=0.8)
    ax.set_xlabel('Training Step', fontsize=12)
    ax.set_ylabel('Loss', fontsize=12)
    ax.set_title('Training Loss Evolution', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Ajouter des statistiques
    min_loss = min(data['loss'])
    max_loss = max(data['loss'])
    final_loss = data['loss'][-1]

    stats_text = f"Min Loss: {min_loss:.4f}\nMax Loss: {max_loss:.4f}\nFinal Loss: {final_loss:.4f}"
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
            fontsize=10)

    plt.tight_layout()
    output_path = f'{output_dir}/training_loss.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Graphique sauvegardé: {output_path}")
    plt.close()

    # Statistiques résumées
    print("\n=== Statistiques d'entraînement ===")
    print(f"Nombre de steps: {len(data['step'])}")
    print(f"Nombre d'epochs: {data['epoch'][-1]:.2f}")
    print(f"Loss initiale: {data['loss'][0]:.4f}")
    print(f"Loss finale: {data['loss'][-1]:.4f}")
    print(f"Loss minimale: {min(data['loss']):.4f}")
    print(f"Loss maximale: {max(data['loss']):.4f}")
    print(f"Amélioration: {((data['loss'][0] - data['loss'][-1]) / data['loss'][0] * 100):.2f}%")
    print(f"Accuracy initiale: {data['mean_token_accuracy'][0]:.4f}")
    print(f"Accuracy finale: {data['mean_token_accuracy'][-1]:.4f}")
    print(f"Learning rate max: {max(data['learning_rate']):.2e}")

if __name__ == '__main__':
    import argparse
    import sys
    import glob

    parser = argparse.ArgumentParser(
        description="Génère des graphiques à partir des logs de fine-tuning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Utiliser le dernier dossier de training
  python plot_training_logs.py

  # Spécifier un dossier de training
  python plot_training_logs.py --output-dir Apertus-FT/output/apertus_lora_combined_20251107_123456

  # Utiliser l'ancien format de fichier
  python plot_training_logs.py --log-file training_loss_logs.txt
        """
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        help="Répertoire contenant training_logs.jsonl (auto-détecte le dernier si non spécifié)"
    )

    parser.add_argument(
        '--log-file',
        type=str,
        help="Fichier de log spécifique (ancien format)"
    )

    args = parser.parse_args()

    # Déterminer le fichier de log à utiliser
    log_file = None

    if args.log_file:
        # Utiliser le fichier spécifié
        log_file = args.log_file
    elif args.output_dir:
        # Chercher training_logs.jsonl dans le répertoire spécifié
        potential_file = os.path.join(args.output_dir, 'training_logs.jsonl')
        if os.path.exists(potential_file):
            log_file = potential_file
        else:
            # Essayer l'ancien format
            potential_file = os.path.join(args.output_dir, 'training_loss_logs.txt')
            if os.path.exists(potential_file):
                log_file = potential_file
    else:
        # Auto-détecter le dernier dossier de training
        output_dirs = glob.glob('Apertus-FT/output/apertus_lora_combined_*')
        if output_dirs:
            # Trier par date (le nom contient le timestamp)
            latest_dir = sorted(output_dirs)[-1]
            potential_file = os.path.join(latest_dir, 'training_logs.jsonl')
            if os.path.exists(potential_file):
                log_file = potential_file
            else:
                # Essayer l'ancien format
                potential_file = os.path.join(latest_dir, 'training_loss_logs.txt')
                if os.path.exists(potential_file):
                    log_file = potential_file

    if not log_file or not os.path.exists(log_file):
        print("❌ Erreur: Impossible de trouver un fichier de logs")
        print("\nUtilisez --output-dir ou --log-file pour spécifier un fichier")
        print("\nOu assurez-vous qu'un dossier Apertus-FT/output/apertus_lora_combined_* existe")
        sys.exit(1)

    print(f"📂 Lecture du fichier: {log_file}")
    data = parse_log_file(log_file)

    if len(data['step']) == 0:
        print("❌ Aucune donnée trouvée dans le fichier de logs")
        sys.exit(1)

    print(f"✓ {len(data['step'])} entrées chargées")

    # Déterminer le répertoire de sortie
    output_dir = os.path.dirname(log_file) if args.output_dir or args.log_file else os.path.dirname(log_file)

    print(f"\n📈 Création des graphiques dans {output_dir}...")
    plot_training_metrics(data, output_dir=output_dir)

    print("\n✅ Terminé!")
