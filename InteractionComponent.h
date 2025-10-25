#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Engine/Engine.h"
#include "InteractionComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnInteractionStarted, AActor*, InteractedActor);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnInteractionEnded, AActor*, InteractedActor);

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECTNAME_API UInteractionComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UInteractionComponent();

protected:
    virtual void BeginPlay() override;

public:
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

    // Interaction properties
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interaction")
    float InteractionRange = 200.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interaction")
    bool bShowDebugInfo = false;

    // Current interaction target
    UPROPERTY(BlueprintReadOnly, Category = "Interaction")
    AActor* CurrentInteractionTarget;

    // Interaction functions
    UFUNCTION(BlueprintCallable, Category = "Interaction")
    void Interact();

    UFUNCTION(BlueprintCallable, Category = "Interaction")
    void SetInteractionTarget(AActor* Target);

    UFUNCTION(BlueprintCallable, Category = "Interaction")
    void ClearInteractionTarget();

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Interaction")
    FOnInteractionStarted OnInteractionStarted;

    UPROPERTY(BlueprintAssignable, Category = "Interaction")
    FOnInteractionEnded OnInteractionEnded;

private:
    void FindNearestInteractable();
    void UpdateInteractionTarget(AActor* NewTarget);
};