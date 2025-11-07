# 🎯 Système Prompt - Configuration

## Système Prompt par Défaut

Le script `test.py` utilise **le même système prompt** que celui utilisé pendant le fine-tuning:

```
"You are a helpful AI assistant specialized in data protection and privacy compliance."
```

## Pourquoi C'est Important?

✅ **Cohérence:** Le modèle a été entraîné avec ce prompt spécifique  
✅ **Performance:** Utiliser le même prompt garantit les meilleures performances  
✅ **Spécialisation:** Le prompt reflète la spécialisation du modèle (RGPD, protection des données)

## Où Est-il Défini?

### **Dans le Fine-tuning**
Fichier: `prepare_dataset.py`
```python
messages = [
    {
        "role": "system",
        "content": "You are a helpful AI assistant specialized in data protection and privacy compliance."
    },
    {
        "role": "user",
        "content": question
    }
]
```

### **Dans les Tests**
Fichier: `test.py`
```python
DEFAULT_SYSTEM_PROMPT = "You are a helpful AI assistant specialized in data protection and privacy compliance."
```

## Personnaliser le Système Prompt

### **Option 1: Utiliser le Prompt par Défaut (Recommandé)**
```bash
./test.sh --model <chemin> --question "Votre question"
```
→ Utilise automatiquement le prompt du fine-tuning

### **Option 2: Prompt Personnalisé**
```bash
./test.sh --model <chemin> --question "Votre question" \
    --system-prompt "You are an expert in machine learning."
```

### **Option 3: Modifier le Prompt par Défaut**
Éditez `test.py` ligne 80:
```python
DEFAULT_SYSTEM_PROMPT = "Votre nouveau prompt par défaut"
```

## Exemples de Prompts Alternatifs

### **Généraliste**
```
"You are a helpful AI assistant."
```

### **Technique**
```
"You are an expert software engineer specialized in Python and machine learning."
```

### **Juridique**
```
"You are a legal expert specialized in European data protection law and GDPR compliance."
```

### **Médical**
```
"You are a medical AI assistant specialized in diagnostics and patient care."
```

## Impact sur les Résultats

| Prompt | Impact | Quand l'Utiliser |
|--------|--------|------------------|
| **Prompt du fine-tuning** | ✅ Optimal | Toujours (recommandé) |
| **Prompt généraliste** | ⚠️ Performances réduites | Tests de robustesse |
| **Prompt différent** | ❌ Peut dégrader | Expérimentation uniquement |

## Bonnes Pratiques

1. ✅ **Toujours utiliser le prompt du fine-tuning** pour l'évaluation
2. ✅ **Documenter** tout changement de prompt
3. ✅ **Tester** l'impact avant de changer le prompt par défaut
4. ⚠️ **Éviter** de changer le prompt sans raison valable

## Comparaison BASE vs Fine-tuné

Le modèle de **BASE** utilise son propre système prompt par défaut:
```
"You are Apertus, a helpful assistant created by the SwissAI initiative."
```

Le modèle **fine-tuné** utilise:
```
"You are a helpful AI assistant specialized in data protection and privacy compliance."
```

Cette différence est **normale** et reflète la spécialisation du fine-tuning.

## Vérifier le Prompt Utilisé

Pour voir quel prompt est actuellement utilisé:
```bash
grep "DEFAULT_SYSTEM_PROMPT" test.py
```

## Questions Fréquentes

### **Q: Dois-je changer le système prompt?**
**R:** Non, sauf si vous avez une raison spécifique. Le prompt par défaut est optimisé pour votre fine-tuning.

### **Q: Puis-je utiliser plusieurs prompts?**
**R:** Oui, utilisez `--system-prompt` pour chaque test avec un prompt différent.

### **Q: Le prompt affecte-t-il vraiment les résultats?**
**R:** Oui! Le modèle a été entraîné avec un prompt spécifique et performe mieux avec celui-ci.

### **Q: Comment tester l'impact d'un prompt différent?**
**R:** Utilisez le mode comparaison:
```bash
# Avec prompt par défaut
./test.sh --model <chemin> --question "Test" > result1.txt

# Avec prompt personnalisé
./test.sh --model <chemin> --question "Test" --system-prompt "Autre prompt" > result2.txt

# Comparer
diff result1.txt result2.txt
```

## Résumé

- 🎯 **Prompt par défaut:** Spécialisé en protection des données
- ✅ **Recommandation:** Toujours utiliser le prompt du fine-tuning
- 🔧 **Personnalisation:** Possible via `--system-prompt`
- 📊 **Impact:** Significatif sur la qualité des réponses
