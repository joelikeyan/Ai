#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SphereComponent.h"
#include "Components/WidgetComponent.h"
#include "CoffeeMachine.generated.h"

UENUM(BlueprintType)
enum class ECoffeeState : uint8
{
    Idle,
    Brewing,
    Ready,
    NeedsSugar
};

UCLASS()
class YOURPROJECTNAME_API ACoffeeMachine : public AActor
{
    GENERATED_BODY()

public:
    ACoffeeMachine();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

    // Coffee machine state
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Coffee Machine")
    ECoffeeState CurrentState = ECoffeeState::Idle;

    // Components
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    class UStaticMeshComponent* MachineMesh;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    class USphereComponent* InteractionSphere;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    class UWidgetComponent* PromptWidget;

    // Coffee properties
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Coffee Machine")
    float BrewTime = 3.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Coffee Machine")
    bool bHasSugar = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Coffee Machine")
    int32 CoffeeCount = 0;

    // Interaction functions
    UFUNCTION(BlueprintCallable, Category = "Coffee Machine")
    void StartBrewing();

    UFUNCTION(BlueprintCallable, Category = "Coffee Machine")
    void AddSugar();

    UFUNCTION(BlueprintCallable, Category = "Coffee Machine")
    void CancelBrewing();

    UFUNCTION(BlueprintCallable, Category = "Coffee Machine")
    void CollectCoffee();

    // Events
    DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnCoffeeStateChanged, ECoffeeState, NewState);
    UPROPERTY(BlueprintAssignable, Category = "Coffee Machine")
    FOnCoffeeStateChanged OnCoffeeStateChanged;

    DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnCoffeeBrewed, int32, CoffeeAmount);
    UPROPERTY(BlueprintAssignable, Category = "Coffee Machine")
    FOnCoffeeBrewed OnCoffeeBrewed;

private:
    float BrewTimer = 0.0f;
    bool bIsBrewing = false;

    void UpdateState(ECoffeeState NewState);
    void UpdatePromptVisibility();
};