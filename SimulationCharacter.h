#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "Components/InputComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SphereComponent.h"
#include "InteractionComponent.h"
#include "SimulationCharacter.generated.h"

UCLASS()
class YOURPROJECTNAME_API ASimulationCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    ASimulationCharacter();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;
    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

    // Interaction functions
    UFUNCTION(BlueprintCallable, Category = "Interaction")
    void Interact();

    UFUNCTION(BlueprintCallable, Category = "Interaction")
    void Grab();

    // Components
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    class UInteractionComponent* InteractionComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    class UStaticMeshComponent* GrabMesh;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    class USphereComponent* GrabCollision;

    // Input mappings
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Input")
    FName InteractActionName = "Interact";

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Input")
    FName GrabActionName = "Grab";

    // Current grabbed object
    UPROPERTY(BlueprintReadOnly, Category = "Interaction")
    AActor* GrabbedActor;

    // Grab location
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interaction")
    FVector GrabOffset = FVector(100.0f, 0.0f, 0.0f);

private:
    void OnInteractPressed();
    void OnGrabPressed();
    void OnGrabReleased();
};