#from django.db import models

# Create your models here.




#class CodeGeneration(models.Model):
#    description = models.CharField(max_length=255)
#    generated_code = models.TextField()

#    def __str__(self):
#        return self.description
from django.db import models

class CodeGeneration(models.Model):
    description = models.TextField()
    generated_code = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of creation

    def __str__(self):
        return f"Description: {self.description[:20]}... | Generated Code: {self.generated_code[:20]}..."
